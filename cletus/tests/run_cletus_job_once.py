#!/usr/bin/env python
""" Used for testing the cletus_job library.

    See the file "LICENSE" for the full license governing use of this file.
    Copyright 2013, 2014 Ken Farmer
"""
from __future__ import absolute_import
from __future__ import print_function



# IMPORTS -----------------------------------------------------------------
import sys
import os
import time
import tempfile
import envoy
import pytest
import argparse

sys.path.insert(0,
os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import cletus.cletus_job as  mod


def main():
    args    = get_args()
    my_test = TestJobCheck(args.lock_wait,
                           args.post_lock_sleep)
    if my_test.lock_process():
        print('locked')
        print('new_pid:%s' % my_test.new_pid)
        return 0
    else:
        print('not-locked')
        return 1


class TestJobCheck(object):

    def __init__(self,
                 lock_wait,
                 post_lock_sleep):

        self.app_name             = 'foo'
        self.lock_wait            = lock_wait
        self.post_lock_sleep      = post_lock_sleep
        self.pid_dir              = os.path.dirname(os.path.realpath(__file__))
        self.new_pid              = None
        assert os.path.isdir(self.pid_dir)

    def lock_process(self):
        my_jobcheck  = mod.JobCheck(app_name=self.app_name,
                                    pid_dir=self.pid_dir)
        self.new_pid = my_jobcheck.new_pid
        lock_result  = my_jobcheck.lock_pidfile(wait_max=self.lock_wait)
        #print 'lock_result: %s' % lock_result
        #print isinstance(lock_result, bool)
        if lock_result:
            time.sleep(self.post_lock_sleep)
            my_jobcheck.close()

        return lock_result


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lock-wait',
                        type=small_positive_numbers,
                        required=True)
    parser.add_argument('--post-lock-sleep',
                        type=small_positive_numbers,
                        required=True)
    args = parser.parse_args()
    return args


def small_positive_numbers(value):
    try:
        ival = int(value)
    except TypeError:
        raise TypeError('%s is not a valid integer' % value)
    if  0 <= ival <= 100:
        return ival
    else:
        raise TypeError('%s is not a small integer between 1 & 100' % value)



if __name__ == '__main__':
    sys.exit(main())
