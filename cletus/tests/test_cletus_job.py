#!/usr/bin/env python
""" Used for testing the cletus_job library.

    See the file "LICENSE" for the full license governing use of this file.
    Copyright 2013, 2014 Ken Farmer
"""



# IMPORTS -----------------------------------------------------------------
import sys
import os
import time
import tempfile
import glob
import shutil
import envoy
import pytest

sys.path.insert(1, '../')

#import cletus.cletus_job as  mod
import cletus_job as  mod


print '\n\nNote: code being tested will produce some messages to ignore\n'


def get_file_pid(temp_dir, pid_fn='*.pid'):

    pid_files = glob.glob(os.path.join(temp_dir, pid_fn))
    with open(pid_files[0], 'r') as f:
        file_pid = int(f.read())
    return pid_files, file_pid


def write_file_pid(pid_fqfn, pid=123456):
    with open(pid_fqfn, 'w') as f:
        f.write(str(pid))
    return pid



class TestJobCheck(object):

   def setup_method(self, method):
       self.temp_dir = tempfile.mkdtemp()
       self.mnemonic = 'foo'
       self.pid_fqfn = os.path.join(self.temp_dir, '%s.pid' % self.mnemonic)
       self.c        = envoy.connect("sleep 4")

   def teardown_method(self, method):
       shutil.rmtree(self.temp_dir)
       self.c.kill()


   def test_no_running_process(self):
       """ Ensure everything works correctly for the most common case - in
           which there is no pre-existing app still running, and no orphaned
           pidfile.
       """
       my_jobcheck = mod.JobCheck(config_dir=self.temp_dir,
                                  mnemonic=self.mnemonic)
       pid_files, file_pid = get_file_pid(self.temp_dir)
       assert my_jobcheck.get_old_job_age() == 0
       assert len(pid_files) == 1
       assert file_pid == my_jobcheck.new_pid


   def test_running_process(self):
       """ Ensure everything works correctly with a pre-existing running
           process.
       """
       pid    = str(self.c.pid)
       with open(self.pid_fqfn, 'w') as f:
            f.write(pid)

       time.sleep(1)
       my_jobcheck = mod.JobCheck(config_dir=self.temp_dir,
                                  mnemonic=self.mnemonic)
       old_job_age = my_jobcheck.get_old_job_age()
       assert 10 > old_job_age > 0
       pid_files, file_pid = get_file_pid(self.temp_dir)
       assert len(pid_files) == 1
       assert file_pid == my_jobcheck.old_pid


   def test_orphaned_process(self):
       """ Tests if create_pid_file() correctly handles a pidfile with no
           running process associated with its PID.
       """

       # first - create a pidfile:
       test_pid    = 39578340
       try:
           os.kill(test_pid, 0)
           print 'made-up pid already exists - will interfere with test - rerun'
           sys.exit(1)
       except OSError:
           pass  # expected result for non-existing process
       with open(self.pid_fqfn, 'w') as f:
           f.write(str(test_pid))

       # next - run and see how it's interpreted:
       my_jobcheck = mod.JobCheck(config_dir=self.temp_dir,
                                  mnemonic=self.mnemonic)
       old_job_age = my_jobcheck.get_old_job_age()
       pid_files, file_pid = get_file_pid(self.temp_dir)
       assert old_job_age    == 0
       assert file_pid       == my_jobcheck.new_pid
       assert len(pid_files) == 1


   def test_running_process_with_empty_pidfile(self):
       """ Ensure everything works correctly with a pre-existing running
           process - that has an empty pidfile.
       """
       with open(self.pid_fqfn, 'w') as f:
            f.write('')

       time.sleep(1)
       with pytest.raises(IOError):
           my_jobcheck = mod.JobCheck(config_dir=self.temp_dir,
                                      mnemonic=self.mnemonic)


