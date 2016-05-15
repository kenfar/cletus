#!/usr/bin/env python
""" Used to ensure that only one job runs at a time.

    Cletus_job is highly opinionated about how to ensure only one job
    at a time runs, when that's important.
       - Applications shouldn't just be told that they can't run because
         another instance is already running.  They should also be informed
         of how long that other instance has been running.  Because sometimes
         an application is eternally waiting on resources, in an endless loop,
         etc.  Knowing that an app has been waiting 8 hours when it should
         never wait more than 5 minutes is useful.
       - Applications should be able to wait for some amount of time for
         the older instance to complete.
       - Just checking on a pid in a file isn't enough: that pid might be
         orphaned.
       - When a file system becomes full, a pidfile could be cataloged,
         but no pid can be written to it.  This needs to be handled.

    So cletus_job's objective is to make it extremely easy for most apps to
    handle this problem.

    It's not yet done - it needs an flock on the pidfile.  But it's almost
    there.

    See the file "LICENSE" for the full license governing use of this file.
    Copyright 2013, 2014 Ken Farmer
"""


import os
import errno
import time
import fcntl

import appdirs
import logging


class RestartError(Exception):
      pass


class JobCheck(object):
    """ Ensures that only 1 job at a time runs.

    Typical Usage:
        job_check    = mod.JobCheck(pgm_name)
        if not job_check.check_old_pidfile(restart=False)
            print 'Critical Error: prior process failed - research'
        elif job_check.lock_pidfile():
            print 'Lock acquired, will start processing'
        else:
            print 'Try again later, already running'

        *** at end of program ***
        job_check.close()

    Inputs:
        app_name (str) - Used to automatically determine pid directory based on xdg
                         standards.  Defaults to None.
        nickname (str) - used for name of pidfile.  Different nicknames allow
                         the same program to be run concurrently.  This might be desirable
                         if there are different config files, and the program can run with
                         only 1 instance per config file at a time.   Defaults to
                         'main'.
        log_name (str) - Should be passed from caller in order to ensure logging
                         characteristics are inherited correctly.  Defaults to __main__.
        pid_dir (str)  - Can be used instead of the automatic XDG directory
                         user_cache_dir, which is useful for testing among other things.
                         Defaults to None - which is fine as long as app_name is provided.

    Raises:
        ValueError   - Neither app_name nor pid_dir was provided, one must be
        OSError      - Could not create pid dir and it didn't already exist
    """

    def __init__(self,
                 app_name=None,
                 nickname='main',
                 log_name='__main__',
                 pid_dir=None):

        self.logger   = logging.getLogger('%s.cletus_job' % log_name)
        # con't print to sys.stderr if no parent logger has been set up:
        #logging.getLogger(log_name).addHandler(logging.NullHandler())
        self.logger.debug('JobCheck starting now')

        # set up config/pidfile directory:
        self.nickname    = nickname
        self.pid_dir     = self._get_pid_dir(app_name, pid_dir)
        self.pid_fqfn    = os.path.join(self.pid_dir, '%s.pid' % self.nickname)

        self.new_pid     = os.getpid()
        self.start_time  = time.time()




    def lock_pidfile(self, wait_max=60):
        """
        Inputs:
           wait_max (int) - Maximum number of seconds for Jobcheck to keep retrying
                            lock acquisition.  If it exceeds this number it will raise a
                            RestartError.  Defaults to 60.
        Returns:
           True      - if lock was acquired
           False     - if lock was not acquired - pidfile is already locked
        Raises:
           WaitError - if file locking takes too long
           IOError   - if pidfile is inaccessable
        """
        while not self._create_locked_pidfile(self.pid_fqfn, self.new_pid):
            if (time.time() - self.start_time) > wait_max:
                self.logger.error('wait_max exceeded, returning without lock')
                return False
            else:
                self.logger.warning('sleeping - waiting for lock')
                time.sleep(0.5)

        self.logger.debug('lock acquired - will return to caller')
        return True


    def _create_locked_pidfile(self, pid_fqfn, pid):
        """ Opens the pidfile, locks it, and writes the pid to it.
            Inputs:
                - pid_fqfn
                - pid
            Returns
                - True    - if locking was successful
                - False   - if locking was unsuccessful
            Raises
                - IOError - if file was inaccessible
        """
        try:
            self.pidfd = open(pid_fqfn, 'a')
        except IOError, e:
            self.logger.critical('Could not open pidfile: %s - permissions? missing dir?' % e)
            raise
        else:
            try:
                fcntl.flock(self.pidfd, fcntl.LOCK_EX|fcntl.LOCK_NB)
            except IOError:
                self.pidfd.close()
                return False
            else:
                self.pidfd.seek(0)
                self.pidfd.truncate()
                self.pidfd.write(str(pid))
                self.pidfd.flush()
                self.old_pid     = 0
                self.old_pid_age = 0
                return True




    def check_old_pidfile(self, restart_ok=True):
        """
        Inputs:
            restart_ok
        restart_ok (bool) - Allows program to automatically overwrite any existing
                            pidfile *if* that pid is not running in the system.  Defaults
                            to True.
        Returns:
            old_pid_age
                    - 0 = no pid file
                          or pid file, no active process & restart=true
                    - > 0 = running process
        Raises:
            RestartError - orphaned pidfile but restart_ok is False
            OSError - problem accessing or deleting pidfile
            IOError - problem accessing pidfile
        """
        self.old_pid         = self._get_old_pid(self.pid_fqfn)
        self.old_pid_age     = self._get_old_pid_age(self.pid_fqfn)

        assert ((self.old_pid == 0 and self.old_pid_age == 0)
             or (self.old_pid > 0 and self.old_pid_age > 0))

        if self.old_pid_age:
            if self._is_old_pid_active():
                self.logger.warning('WARNING: active process still running')
            else:
                if restart_ok:
                    self.logger.warning('no old process running - will delete old pidfile')
                    self._delete_pidfile()
                    self.old_pid     = 0
                    self.old_pid_age = 0
                else:
                    self.logger.error('no old process running - restart_ok not on, quitting')
                    raise RestartError, 'pidfile left behind by old process, restart_ok not on, quitting'
        return self.old_pid_age


    def _get_old_pid_age(self, file_name):
        """ Returns the duration of the existing pidfile in seconds.
            If the duration is less than 1 second, will still return 1.
            If no pidfile exists, will return 0.
        """
        try:
            return max(1, time.time() - os.path.getmtime(file_name))
        except OSError as exception:
            if exception.errno == errno.ENOENT:
                print 'unable to find filename: %s' % file_name
                return 0   # no file exists
            else:
                self.logger.critical('_get_old_pide_age encountered IO Error')
                raise

    def _get_old_pid(self, pid_fqfn):
        """ Out of space conditions may allow the file to be cataloged, but
            no data written.   If this happens the function will print a
            message and raise an exception.
            Inputs
            Returns
                - pid from within file or 0 if no pidfile exists
        """
        try:
            with open(pid_fqfn, 'r') as f:
                return int(f.read())
        except IOError as exception:
            # this is normal - if no prior pidfile exists
            if exception.errno == errno.ENOENT:
                return 0
            else:
                self.logger.critical('cannot access pidfile - permissions? wrong dir?')
                raise
        except ValueError:
            self.logger.critical('empty pidfile found!')
            self.logger.critical('Prior process probably ran out of disk')
            raise IOError, 'Empty pidfile found - process probably ran out of space'


    def _is_old_pid_active(self):
        """ Checks to see if pid is still running
            Returns True/False
            Should be able to deal with 0 pid for non-existing files just fine
        """
        try:
            os.kill(self.old_pid, 0)
        except OSError:
            self.logger.warning('program has a pidfile but is not currently running')
            return False
        else:
            self.logger.warning('program already running')
            return True




    def _delete_pidfile(self):
        """ Deletes pidfile if it exists.
            Handles non-existing files.
        """
        self.pidfd.close()
        try:
            os.remove(self.pid_fqfn)
        except OSError as e:
            if e.errno != errno.ENOENT:
                self.logger.critical('_delete_pidfile encountered IO error: %s' % e)
                raise


    def close(self):
        """ Final user interaction with class.
            Class can recover from prior jobs not doing this - but it's sloppy
            and could hypothetically result in errors.

        """
        if self.old_pid:
            self.logger.warning('close() should not be called when old job already exists. Will ignore.')
        else:
            self._delete_pidfile()



    def _get_pid_dir(self, app_name, arg_pid_dir):

        # first figure out what the directory is:
        if arg_pid_dir:
            pid_dir  = arg_pid_dir
            self.logger.debug('pid_dir will be based on arg: %s' % arg_pid_dir)
        else:
            if app_name:
                pid_dir  = os.path.join(appdirs.user_cache_dir(app_name), 'jobs')
                self.logger.debug('pid_dir will be based on user_cache_dir: %s' % pid_dir)
            else:
                err_msg = 'app_name must be provided if pid_dir is not'
                self.logger.critical(err_msg)
                raise ValueError, err_msg

        # next try to create it, just in case it isn't there
        try:
            os.makedirs(pid_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                self.logger.critical('Error trying to access pid_dir: %s' % pid_dir)
                raise

        # finally, return it
        return pid_dir

