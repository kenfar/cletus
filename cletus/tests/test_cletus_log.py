#!/usr/bin/env python
"""
    Used to test cletus_log

    See the file "LICENSE" for the full license governing use of this file.
        Copyright 2013, 2014 Ken Farmer
"""


# IMPORTS -----------------------------------------------------------------
import sys
import os
import time
import shutil
import tempfile
import pytest
import fileinput


sys.path.insert(0,
os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import cletus.cletus_log  as mod




#print '\n\nNote: code being tested will produce some messages to ignore\n'



class TestBasicLog(object):

    def setup_method(self, method):
        self.temp_dir = tempfile.mkdtemp()
        self.log_mgr  = mod.LogManager(app_name='main',
                                       log_dir=self.temp_dir,
                                       log_fn='test.log',
                                       log_to_console=False)
        self.logger   = self.log_mgr.logger
        self.logger.setLevel('DEBUG')


    def teardown_method(self, method):
        shutil.rmtree(self.temp_dir)


    def test_format_of_1_line(self):

        # something isn't writing rows out for python 2.6
        if sys.version_info[:2] == (2, 6):
            return

        self.logger.info('Test1')

        for rec in fileinput.input(os.path.join(self.temp_dir, 'test.log')):
            pass

        assert fileinput.lineno() == 1
        fields = rec.split(':')
        assert fields[1].strip() == '__main__'
        assert fields[2].strip() == 'INFO'
        assert fields[3].strip() == 'Test1'





