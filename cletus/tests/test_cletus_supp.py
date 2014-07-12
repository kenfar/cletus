#!/usr/bin/env python
""" Used for testing the cletus_supp module.

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
from pprint import pprint as pp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import cletus.cletus_supp as  mod

print '\nNote: code being tested will produce some messages to ignore'


def write_suppression_file(suppress_dir,
                           suppress_name):
    suppress_fqfn = os.path.join(suppress_dir, 'name-%s.suppress' % suppress_name)
    with open(suppress_fqfn, 'w') as f:
        f.write('')


class TestValidSuppressFile(object):

   def test_extensions(self):
       assert mod._valid_suppress_file('name-foo.suppress')          is True
       assert mod._valid_suppress_file('name-foo.suppress.suppress') is True
       assert mod._valid_suppress_file('name-foo.buckbuck.suppress') is True
       assert mod._valid_suppress_file('name-foo.bar')               is False
       assert mod._valid_suppress_file('name-foo.suppress.bar')      is False
       assert mod._valid_suppress_file('name-foo.buckbuck.SUPPRESS') is False

   def test_filename(self):
       assert mod._valid_suppress_file('name-foo.suppress')          is True
       assert mod._valid_suppress_file('NAME-foo.suppress')          is False
       assert mod._valid_suppress_file('/name-pho/foo.suppress')     is False
       assert mod._valid_suppress_file('foo.bar')                    is False

   def test_path(self):
       assert mod._valid_suppress_file('blah/name-foo.suppress')     is True
       assert mod._valid_suppress_file('/blah/name-foo.suppress')    is True
       assert mod._valid_suppress_file('/name-pho/foo.suppress')     is False



class TestSuppressCheck(object):

   def setup_method(self, method):
       self.temp_parent_dir = tempfile.mkdtemp()
       self.temp_dir        = os.path.join(self.temp_parent_dir, 'suppress')
       os.mkdir(self.temp_dir)
       self.app_name = 'foo'

   def teardown_method(self, method):
       shutil.rmtree(self.temp_parent_dir)

   def test_no_suppressions(self):
       """ Confirm that nothing gets suppressed when the suppression dir
           is empty.
       """
       suppcheck = mod.SuppressCheck(self.app_name,
                                     config_dir=self.temp_parent_dir)
       assert not suppcheck.suppressed()
       assert not suppcheck.suppressed('bar')

   def test_all_suppression(self):
       """ Confirm that all names are suppressed when this file exists in
           suppression dir:   'name-all.suppress'
       """
       print 'testing temp_dir: %s' % self.temp_dir
       write_suppression_file(self.temp_dir, 'all')
       suppcheck = mod.SuppressCheck(self.app_name,
                                     config_dir=self.temp_parent_dir)
       assert suppcheck.suppressed()
       assert suppcheck.suppressed('bar')

   def test_some_suppression(self):
       """ Confirm that only matching names are suppressed when a non-all
           suppression file exists.
       """
       write_suppression_file(self.temp_dir, 'foo')
       suppcheck = mod.SuppressCheck(self.app_name,
                                     config_dir=self.temp_parent_dir)
       assert suppcheck.suppressed('bar') is False
       assert suppcheck.suppressed('foo') is True
       assert suppcheck.suppressed()      is True

   def test_invalid_suppression_file(self):
       """ Confirm invalid files are handled right.
       """
       suppress_fqfn = os.path.join(self.temp_dir, 'blah.suppress')
       with open(suppress_fqfn, 'w') as f:
           f.write('')
       suppcheck = mod.SuppressCheck(self.app_name,
                                     config_dir=self.temp_parent_dir)
       with pytest.raises(ValueError):
            suppcheck.suppressed()





