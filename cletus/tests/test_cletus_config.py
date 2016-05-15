#!/usr/bin/env python
""" Used for testing the cletus_job library.

    See the file "LICENSE" for the full license governing use of this file.
    Copyright 2013, 2014, 2015, 2016 Ken Farmer
"""
from __future__ import absolute_import


# IMPORTS -----------------------------------------------------------------
import sys
import os
import tempfile
import shutil
import pytest
import argparse
import yaml
from os.path import dirname, basename, isfile, isdir, exists
from pprint import pprint as pp

sys.path.insert(0, dirname(dirname(dirname(os.path.abspath(__file__)))))
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
        #self.var_list.append('HOME')  # test fails with tox, but works with pytest

    def test_add_vars_using_arg_list(self):
        self.config_man.add_env_vars(self.var_list)
        pp(self.config_man.cm_config_env)
        assert self.config_man.cm_config_env['CLETUS_FOO'] == 'bar'
        #assert 'HOME' in self.config_man.cm_config_env # test fails with tox, but works with pytest

    def test_add_vars_using_schema(self):
        config_man = mod.ConfigManager(config_schema=self.config_schema)
        config_man.add_env_vars()
        pp(config_man.cm_config_env)
        assert config_man.cm_config_env['CLETUS_FOO'] == 'bar'
        #assert 'HOME' in config_man.cm_config_env   # test fails with tox, but works with pytest

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
        assert list(self.config_man.cm_config.keys()) == []


class Test_add_iterables_twice(object):
    """ Confirms that adding a second iterable doesn't include anything
        from the first.
    """
    def setup_method(self, method):
        self.config_man = mod.ConfigManager()

    def test_second_iterable_overrides_entries_from_first(self):
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

    def test_nones_from_second_iterable_do_not_override_entries_from_first(self):
        # first update with all args:
        first_dict = { 'foo':'somefoo',
                       'bar':'emptiness',
                       'baz':None  }
        self.config_man.add_iterable(first_dict)

        # second update with just 1 args:
        second_dict = { 'foo':None,
                        'bar':'somebar',
                        'baz':'somebaz'}
        self.config_man.add_iterable(second_dict)

        # confirm that second iterative-add didn't pick up baz from first:
        assert self.config_man.cm_config['foo'] == 'somefoo'
        assert self.config_man.cm_config['bar'] == 'somebar'
        assert self.config_man.cm_config['baz'] == 'somebaz'

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
        assert list(config_man.cm_config.keys()) == []



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
    def setup_method(self, method):
        self.schema = {'type': 'object',
                       'properties': {
                         'foo':  {'required': True, 'type':     'string'},
                         'baz':  {'enum': ['spaz','fads']} },
                       'additionalProperties': False }
        self.config_man = mod.ConfigManager(self.schema)

    def test_good_config(self):
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

    def test_type_checking_with_nulls(self):
        self.schema = {'type': 'object',
                       'properties': {
                         'foo':  {'type':  ['integer', 'null']} } }
        self.config_man = mod.ConfigManager(self.schema)

        # confirm integers work
        self.config_man.add_iterable({'foo':5})
        self.config_man.validate()

        # confirm None works
        self.config_man = mod.ConfigManager(self.schema)
        self.config_man.add_iterable({'foo':None})
        self.config_man.validate()

        # confirm it rejects strings
        with pytest.raises(ValueError):
            self.config_man = mod.ConfigManager(self.schema)
            self.config_man.add_iterable({'foo':'Bad Data'})
            self.config_man.validate()






class Test_validation_schema(object):

    def test_extra_fields_in_validation_schema(self):
        self.schema = {'type': 'object',
                       'properties': {
                           'foo':  {'required': True,
                                    'type':     'string',
                                    'foo':      'bar'},
                           'baz':  {'enum': ['spaz','fads']} },
                       'additionalProperties': False }
        self.config_man = mod.ConfigManager(self.schema)

        sample_dict = {}
        sample_dict['foo']  = 'bar'
        sample_dict['baz']  = 'spaz'
        self.config_man.add_iterable(sample_dict)
        assert self.config_man.validate() is True

    def test_items_title_and_desc(self):
        """ Show we can include title & desc columns without breakig anything
        """
        self.schema = {'type': 'object',
                       'title': 'config',
                       'description': 'the config validation schema',
                       'properties': {
                           'results': {
                                'items': [
                                        {"type": "integer",
                                         "title": "field1",
                                         "description": "blahblahblah" },
                                        {"type": "string"} ] } } }
        self.config_man = mod.ConfigManager(self.schema)
        sample_dict = {}
        sample_dict["results"] = [1, "foo"]
        self.config_man.add_iterable(sample_dict)
        assert self.config_man.validate() is True

    def test_using_properties_title_desc_and_default(self):
        """ Show we can include title, desc, default columns without breakig anything
        """
        self.schema = {'type': 'object',
                       'title': 'config',
                       'description': 'the config validation schema',
                       'properties': {
                           'foo':  {'required':    True,
                                    'blank':       True,
                                    'type':        'string',
                                    'title':       'foo-title',
                                    'description': 'foo-desc',
                                    'default':     'bar'},
                           'baz':  {'enum': ['spaz','fads']} },
                       'additionalProperties': False }
        self.config_man = mod.ConfigManager(self.schema)
        sample_dict = {}
        sample_dict['foo']  = 'string'
        sample_dict['baz']  = 'spaz'
        self.config_man.add_iterable(sample_dict)
        assert self.config_man.validate() is True


class Test_add_defaults(object):
    def setup_method(self, method):
        self.schema = {'type': 'object',
                       'properties': {
                         'foo':  {'type':    ['null', 'string']},
                         'baz':  {'type':    'string'} },
                       'additionalProperties': False } 
        self.defaults = {'foo':  'foostuff'}
        self.config_man = mod.ConfigManager(self.schema)

    def test_populated_config_has_no_changes(self):
        sample_dict = {}
        sample_dict['foo']  = 'bar'
        sample_dict['baz']  = 'spaz'
        self.config_man.add_iterable(sample_dict)
        assert self.config_man.validate() is True
        self.config_man.add_defaults(self.defaults)
        assert self.config_man.validate() is True
        assert self.config_man.cm_config['foo'] == 'bar'
        assert self.config_man.cm_config['baz'] == 'spaz'

    def test_unpopulated_config_is_changed(self):
        sample_dict = {}
        sample_dict['foo']  = None
        sample_dict['baz']  = 'spaz'
        self.config_man.add_iterable(sample_dict)
        assert self.config_man.validate() is True
        self.config_man.add_defaults(self.defaults)
        assert self.config_man.validate() is True
        assert self.config_man.cm_config['foo'] == 'foostuff'
        assert self.config_man.cm_config['baz'] == 'spaz'



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



