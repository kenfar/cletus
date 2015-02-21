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
import fcntl
from os.path import dirname, basename, isfile, isdir, exists

sys.path.insert(0, dirname(dirname(dirname(os.path.abspath(__file__)))))
import cletus.cletus_job  as mod

test_path = dirname(os.path.realpath((__file__)))



print '\n\nNote: code being tested will produce some messages to ignore\n'


def get_file_pid(temp_dir, pid_fn='*.pid'):

    pid_files = glob.glob(os.path.join(temp_dir, pid_fn))
    print pid_files
    with open(pid_files[0], 'r') as f:
        print '================ pid contents: ================ '
        print f.read()
        file_pid = int(f.read())
    return pid_files, file_pid


def write_file_pid(pid_fqfn, pid=123456):
    with open(pid_fqfn, 'w') as f:
        f.write(str(pid))
    return pid



class TestPidFile(object):

    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    def test_correct_pid(self):
        pass
        # run jobcheck directly
        # read pidfile       

    def test_delete_pidfile(self):
        pass
        # run jobcheck directly
        # read pidfile       





class TestCompetingJobs(object):

    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    def test_single_process(self):

       # confirm it locks & responds right in the
       # simplest case.
       cmd1     = '''%s/run_cletus_job_once.py     \
                       --lock-wait 1               \
                       --post-lock-sleep 1         \
                  ''' % test_path
       self.c1   = envoy.run(cmd1)
       assert self.c1.status_code == 0 # locked


    def test_single_asynch_process(self):
       """ Objective is to confirm that this method of 
           running the job will work correctly.
       """

       cmd1     = '''%s/run_cletus_job_once.py     \
                       --lock-wait 1               \
                       --post-lock-sleep 1         \
                  ''' % test_path
       #--------------------------------------------
       # note that due to a bug in envoy, you must 
       # block before you can check the status_code
       #-------------------------------------------
       self.c   = envoy.connect(cmd1)
       self.c.block() 
       assert self.c.status_code == 0 # locked


    def test_two_asynch_running(self):

       #---- get lock & hold it
       cmd1     = '''%s/run_cletus_job_once.py  \
                       --lock-wait  0           \
                       --post-lock-sleep 3      \
                  ''' % test_path
       self.c   = envoy.connect(cmd1)

       #---- ensure cmd1 locks file before cmd2 starts!
       time.sleep(0.5)

       #---- try to get lock, fail, quit fast 
       cmd2     = '''%s/run_cletus_job_once.py   \
                       --lock-wait  0            \
                       --post-lock-sleep 0       \
                  ''' % test_path
       self.c2  = envoy.connect(cmd2)

       #---- finish cmd2, then finish cmd1
       self.c.block()
       self.c2.block()

       assert self.c.status_code  == 0 # locked
       assert self.c2.status_code != 0 # not-locked


    def test_two_asynch_running_retry_locks(self):

       #--- get lock & hold it
       cmd1     = '''%s/run_cletus_job_once.py   \
                       --lock-wait  0            \
                       --post-lock-sleep 2       \
                  ''' % test_path
       print(cmd1)
       self.c   = envoy.connect(cmd1)

       #---- ensure cmd1 locks file before cmd2 starts!
       time.sleep(0.5)

       #---- try to get lock, wait for it, get it
       cmd2     = '''%s/run_cletus_job_once.py \
                       --lock-wait  3         \
                       --post-lock-sleep 0    \
                  ''' % test_path
       print(cmd2)

       self.c2  = envoy.connect(cmd2)

       #---- finish cmd2, then finish cmd1
       self.c2.block()
       self.c.block()

       assert self.c2.status_code == 0 # locked
       assert self.c.status_code  == 0 # locked
       

