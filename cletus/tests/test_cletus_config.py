#!/usr/bin/env python
""" Used for testing the cletus_job library.

    See the file "LICENSE" for the full license governing use of this file.
    Copyright 2013, 2014 Ken Farmer
"""


# IMPORTS -----------------------------------------------------------------
import sys
import os
import tempfile
import shutil
import pytest
import argparse
import yaml

from pprint import pprint as pp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import cletus.cletus_config  as mod



class Test_add_file(object):

    def setup_method(self, method):
        self.temp_dir = tempfile.mkdtemp()
        config        = {}
        config['foo'] = 'bar'
        config['baz'] = None
        with open(os.path.join(self.temp_dir, 'config.yml'), 'w') as outfile:
           outfile.write( yaml.dump(config, default_flow_style=True) )

    def teardown_method(self, method):
        shutil.rmtree(self.temp_dir)

    def test_basic(self):
        self.config_man = mod.ConfigManager()
        self.config_man.add_file(config_dir=self.temp_dir, config_fn='config.yml')
        assert self.config_man.cm_config_file['foo'] == 'bar'
        assert self.config_man.cm_config['foo'] == 'bar'


class Test_add_env_vars(object):

    def setup_method(self, method):
        self.config_schema = {'type': 'object',
                              'properties': {
                                  'home':       '',
                                  'dir':        '',
                                  'type':       'string',
                                  'cletus_foo': 'foo1'},
                              'additionalProperties': False }

        self.config_man = mod.ConfigManager()
        os.environ['CLETUS_FOO'] = 'bar'
        self.var_list = []
        self.var_list.append('CLETUS_FOO')
        self.var_list.append('HOME')

    def test_add_vars_using_arg_list(self):
        self.config_man.add_env_vars(self.var_list)
        pp(self.config_man.cm_config_env)
        assert self.config_man.cm_config_env['CLETUS_FOO'] == 'bar'
        assert 'HOME' in self.config_man.cm_config_env

    def test_add_vars_using_schema(self):
        config_man = mod.ConfigManager(config_schema=self.config_schema)
        config_man.add_env_vars()
        pp(config_man.cm_config_env)
        assert config_man.cm_config_env['CLETUS_FOO'] == 'bar'
        assert 'HOME' in config_man.cm_config_env

    def test_add_vars_using_no_keys(self):
        config_man = mod.ConfigManager()
        with pytest.raises(ValueError):
            config_man.add_env_vars()

    def test_add_vars_into_final_config(self):
        self.config_man.add_env_vars(self.var_list)
        assert self.config_man.cm_config_env['CLETUS_FOO'] \
            == self.config_man.cm_config['CLETUS_FOO']

    def test_transform_to_lower(self):
        self.config_man.add_env_vars(self.var_list, key_to_lower=True)
        pp(self.config_man.cm_config_env)
        assert self.config_man.cm_config_env['cletus_foo'] == 'bar'
        assert self.config_man.cm_config['cletus_foo']     == 'bar'


class Test_get_schema_keys(object):

    def setup_method(self, method):
        self.config_schema = {'type': 'object',
                              'properties': {
                                  'pythonpath': '',
                                  'dir':        '',
                                  'type':       'string'},
                              'additionalProperties': False }
        self.config_man = mod.ConfigManager(self.config_schema)

    def test_basic_valid_schema(self):
        assert sorted(self.config_man._get_schema_keys()) \
               == sorted(['PYTHONPATH', 'DIR', 'TYPE'])

    def test_empty_schema(self):
        config_man = mod.ConfigManager()
        assert config_man._get_schema_keys() == []


class Test_add_iterable(object):


    def setup_method(self, method):
        self.config_man = mod.ConfigManager()

    def test_dict(self):
        sample_dict = {}
        sample_dict['foo'] = 'bar'
        self.config_man.add_iterable(sample_dict)
        assert self.config_man.cm_config_iterable['foo'] == 'bar'
        assert self.config_man.cm_config['foo'] == 'bar'

    def test_list_of_tuples(self):
        sample_dict = []
        sample_dict.append(('foo','bar'))
        self.config_man.add_iterable(sample_dict)
        assert self.config_man.cm_config_iterable['foo'] == 'bar'
        assert self.config_man.cm_config['foo'] == 'bar'

    def test_empty_dict(self):
        sample_dict = {}
        self.config_man.add_iterable(sample_dict)
        assert self.config_man.cm_config.keys() == []

class Test_add_iterables_twice(object):
    """ Confirms that adding a second iterable doesn't include anything
        from the first.
    """

    def setup_method(self, method):
        self.config_man = mod.ConfigManager()

    def test_dict(self):
        # first update with all args:
        first_dict = { 'foo':'bar',
                       'baz':None  }
        self.config_man.add_iterable(first_dict)

        # next update from, say the config file.  We won't really run the add
        # file job, lets fake it:
        self.config_man.cm_config_file['baz'] = 'durp'
        self.config_man._post_add_maintenance(self.config_man.cm_config_file)

        # confirm that pretend-file-add did overwrite baz:
        assert self.config_man.cm_config_iterable['baz'] is None
        assert self.config_man.cm_config['foo'] == 'bar'
        assert self.config_man.cm_config['baz'] == 'durp'
        assert self.config_man.baz == 'durp'

        # second update with just 1 args:
        second_dict = { 'foo':'gorilla'}
        self.config_man.add_iterable(second_dict)

        # confirm that second iterative-add didn't pick up baz from first:
        assert 'baz' not in self.config_man.cm_config_iterable
        assert self.config_man.cm_config['foo'] == 'gorilla'
        assert self.config_man.cm_config['baz'] == 'durp'
        assert self.config_man.baz == 'durp'


class Test_add_namespace(object):

    def setup_method(self, method):
        parser = argparse.ArgumentParser()
        parser.add_argument('--foo',
                            default='bar')
        parser.add_argument('--pythonpath',
                            default='')
        parser.add_argument('--logdir')

        self.args = parser.parse_args([])
        self.config_man = mod.ConfigManager()

    def test_basic(self):
        self.config_man.add_namespace(self.args)
        assert self.config_man.cm_config_namespace['foo'] == 'bar'
        assert self.config_man.cm_config['foo']        == 'bar'
        assert self.config_man.cm_config['pythonpath'] == ''
        assert self.config_man.cm_config['logdir']     is None

    def test_empty_namespace(self):
        parser     = argparse.ArgumentParser()
        args       = parser.parse_args([])
        config_man = mod.ConfigManager()
        self.config_man.add_namespace(args)
        assert config_man.cm_config.keys() == []



class Test_combination_of_adds(object):
    """ Verifies that subsequent adds will override the prior value.
    """

    def setup_method(self, method):
        self.config_man = mod.ConfigManager()

    def test_three_in_a_row(self):

        #--- an iterable: dictionary ----
        sample_dict = {}
        sample_dict['foo']  = 'bar'
        sample_dict['baz']  = 'spaz'
        sample_dict['bugs'] = 'ant'
        self.config_man.add_iterable(sample_dict)

        #--- an iterable: tuple ----
        tuples = []
        tuples.append(('foo','notabar'))
        self.config_man.add_iterable(tuples)

        #--- a namespace ----
        parser     = argparse.ArgumentParser()
        parser.add_argument('--bugs',
                            default='bear')
        args       = parser.parse_args([])
        self.config_man.add_namespace(args)

        assert sorted(self.config_man.cm_config.keys())  == sorted(['foo','baz','bugs'])
        assert self.config_man.cm_config['foo']  == 'notabar'
        assert self.config_man.cm_config['baz']  == 'spaz'
        assert self.config_man.cm_config['bugs'] == 'bear'


class Test_validation(object):
    """
    """

    def setup_method(self, method):
        self.schema = {'type': 'object',
                       'properties': {
                         'foo':  {'required': True, 'type':     'string'},
                         'baz':  {'enum': ['spaz','fads']} },
                       'additionalProperties': False
                      }
        self.config_man = mod.ConfigManager(self.schema)

    def test_good_config(self):

        #--- an iterable: dictionary ----
        sample_dict = {}
        sample_dict['foo']  = 'bar'
        sample_dict['baz']  = 'spaz'
        self.config_man.add_iterable(sample_dict)

        assert self.config_man.validate() is True

    def test_bad_config(self):

        #--- have omitted a required config item ---
        sample_dict = {}
        sample_dict['baz']  = 'spaz'
        self.config_man.add_iterable(sample_dict)

        with pytest.raises(ValueError):
            self.config_man.validate()


class Test_access_via_namespace(object):


    def setup_method(self, method):
        self.config_man = mod.ConfigManager()

    def test_dict(self):
        sample_dict = {}
        sample_dict['foo'] = 'bar'
        self.config_man.add_iterable(sample_dict)
        assert self.config_man.cm_config_iterable['foo'] == 'bar'
        assert self.config_man.cm_config['foo'] == 'bar'
        assert self.config_man.foo == 'bar'

    def test_invalid_variable_name(self):
        sample_dict = {}
        sample_dict['cm_config'] = 'bar'
        with pytest.raises(ValueError):
            self.config_man.add_iterable(sample_dict)

    def test_invalid_method_name(self):
        sample_dict = {}
        sample_dict['add_file'] = 'bar'
        with pytest.raises(ValueError):
            self.config_man.add_iterable(sample_dict)

