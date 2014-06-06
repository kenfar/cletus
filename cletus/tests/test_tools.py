#!/usr/bin/env python
""" Used as a general aid in testing.

    See the file "LICENSE" for the full license governing use of this file.
    Copyright 2013, 2014 Ken Farmer
"""


import os
import imp
import glob
import tempfile
import shutil

def load_script(script):
    """ Imports script from parent directory.  Has following features:
        - can handle scripts with or without .py suffix
        - should support being run from different directories
    """
    test_dir = os.path.dirname(os.path.realpath(__file__))
    script_dir = os.path.dirname(test_dir)
    py_source_open_mode = "U"
    py_source_description = (".py", py_source_open_mode, imp.PY_SOURCE)
    script_filepath = os.path.join(script_dir, script)
    with open(script_filepath, py_source_open_mode) as script_file:
        mod = imp.load_module(script, script_file, script_filepath, py_source_description)
    return mod


def remove_dir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)


def remove_all_cletus_temp_dirs():
    """ The objective of this code is to eliminate directories left over from prior
        test runs - that crashed before the temp dirs could be removed.
    """
    ###[os.remove(f) for f in glob.glob(os.path.join(self.feed_audit_dir, '*'))]
    for file in glob.glob(os.path.join(tempfile.gettempdir(), 'bfq_*')):
        shutil.rmtree(file)



