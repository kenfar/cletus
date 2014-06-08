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

import appdirs
import logging


class NullHandler(logging.Handler):
    def emit(self, record):
        #print record
        pass


class JobCheck(object):
    """ Ensures that only 1 job at a time runs.

        Typical Usage:
           job_check    = mod.JobCheck(pgm_name)
           old_job_age  = job_check.get_old_job_age()
           if old_job_age:
               print 'WARNING: process already running'
               print '   Old job has been running %d seconds' % old_job_age
               sys.exit(0)

           *** at end of program ***
           job_check.close()

        misc notes:
        - tested via test-harness

        !!!! should use flock !!!!
    """

    def __init__(self,
                 app_name,
                 mnemonic='main',
                 log_name='__main__',
                 config_dir=None):
        """ Does 99% of the work.
            Inputs:
               - app_name - used to determine config directory
               - mnemonic - used for name of pidfile.  Different mnemonics allow
                 the same app to be run for different configs at the same time.
               - log_name - should be passed from caller.
               - config_dir - can be used instead of the automatic XDG directory
                 user_config_dir, which is very useful for testing.
        """
        self.logger   = logging.getLogger('%s.cletus_job' % log_name)
        # con't print to sys.stderr if no parent logger has been set up:
        #logging.getLogger(log_name).addHandler(logging.NullHandler())
        self.logger.debug('JobCheck starting now')

        # set up config/pidfile directory:
        self.mnemonic    = mnemonic
        if config_dir:
            self.config_dir  = os.path.join(config_dir, 'jobs')
            self.logger.debug('config_dir derrived from arg: %s' % self.config_dir)
        else:
            self.config_dir  = os.path.join(appdirs.user_config_dir(app_name), 'jobs')
            self.logger.debug('config_dir provided via user_config_dir: %s' % self.config_dir)
        try:
            os.makedirs(self.config_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        self.pid_fqfn        = os.path.join(self.config_dir, '%s.pid' % self.mnemonic)

        self.new_pid         = os.getpid()
        self.old_pid         = self._get_file_pid()
        self.old_job_age     = self._get_file_age()
        assert ((self.old_pid == 0 and self.old_job_age == 0)
             or (self.old_pid > 0 and self.old_job_age > 0))

        if (self.old_job_age and self._old_pid_active()):
            self.logger.warning('WARNING: active process still running')
        else:
            self.logger.debug('no active process found')
            self._delete_pidfile()
            self.old_pid     = 0
            self.old_job_age = 0
            self._make_pidfile()


    def get_old_job_age(self):
        """ Provides easy method for calling programs to determine if they have
            a green light to go:
                - no inputs
                - returns number of seconds an existing process has been
                  running
            if the output is 0 - then you're good to go
            if the output is > 0 - then don't go - another process is already
            running.
        """
        return self.old_job_age


    def close(self):
        """ Final user interaction with class.
            Class can recover from prior jobs not doing this - but it's sloppy
            and could hypothetically result in errors.

        """
        if self.old_pid:
            self.logger.warning('close() should not be called when old job already exists. Will ignore.')
        else:
            self._delete_pidfile()


    def _get_file_pid(self):
        """ Out of space conditions may allow the file to be cataloged, but
            no data written.   If this happens the function will print a
            message and raise an exception.
        """
        try:
            with open(self.pid_fqfn, 'r') as f:
                return int(f.read())
        except IOError as exception:
            if exception.errno == errno.ENOENT:
                return 0
            else:
                raise
        except ValueError:
            self.logger.critical('empty pidfile found!')
            self.logger.critical('Prior process probably ran out of disk')
            raise IOError


    def _old_pid_active(self):
        """ Checks to see if pid is still running
            Returns True/False
            Should be able to deal with 0 pid for non-existing files just fine
        """
        try:
            os.kill(self.old_pid, 0)
            self.logger.warning('program already running')
            return True
        except OSError:
            self.logger.warning('program has a pidfile but is not currently running')
            return False
        return False


    def _make_pidfile(self):
        """ Creates a pidfile with the new pid inside the file.
        """
        with open(self.pid_fqfn, 'w') as f:
            f.write(str(self.new_pid))


    def _delete_pidfile(self):
        """ Deletes pidfile if it exists.
            Handles non-existing files.
        """
        try:
            os.remove(self.pid_fqfn)
        except OSError as exception:
            if exception.errno != errno.ENOENT:
                self.logger.critical('_delete_pidfile encountered IO error')
                raise


    def _get_file_age(self):
        """ Returns the duration of the existing pidfile in seconds.
            If the duration is less than 1 second, will still return 1.
            If no pidfile exists, will return 0.
        """
        try:
            return max(1, time.time() - os.path.getmtime(self.pid_fqfn))
        except OSError as exception:
            if exception.errno == errno.ENOENT:
                return 0
                self.logger.warning('get_file_age found no file - probably deleted in race condition')
            else:
                self.logger.critical('get_file_age encountered IO Error')
                raise



