#!/usr/bin/env python


# IMPORTS -----------------------------------------------------------------
import sys
import os
import time
import tempfile
import glob
import shutil
import envoy
import pytest
import fileinput

sys.path.insert(1, '../')

import cletus_log as  mod


#print '\n\nNote: code being tested will produce some messages to ignore\n'



class TestBasicLog(object):

    def setup_method(self, method):
        self.temp_dir = tempfile.mkdtemp()
        self.log_mgr  = mod.LogManager(log_dir=self.temp_dir,
                                       log_fn='test.log',
                                       name='main')
        self.logger   = self.log_mgr.get_logger('starting now')
        self.logger.logger.setLevel('DEBUG')

    def teardown_method(self, method):
        shutil.rmtree(self.temp_dir)


    def test_format_of_1_line(self):

        self.logger.info('Test1')

        rec_cnt = 0
        for rec in fileinput.input(os.path.join(self.temp_dir, 'test.log')):
           #print rec
           pass

        assert fileinput.lineno() == 1
        fields = rec.split(':')
        assert fields[1].strip() == 'main'
        assert fields[2].strip() == 'INFO'
        assert fields[3].strip() == 'Test1'





