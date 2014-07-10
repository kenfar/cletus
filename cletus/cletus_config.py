#!/usr/bin/env python
""" Used to manage access to config files.

    Cletus_config is highly opinionated about what constitutes good config
    management:
       - Config files should be kept within the xdg directory:
            - linux:  $HOME/.config/<app name>
       - But overrides to the location, for special runs, migrations,
         testing, etc are occasionally necessary.
       - The best format at present for config files is yaml.
       - Config file contents should be validated.
       - Arguments should override config items.
       - It's easier to reference config items as namespaces than
         dictionaries.

    The objective of cletus_config is to deliver on this optinions in a way
    that makes it easy for applications.

    See the file "LICENSE" for the full license governing use of this file.
    Copyright 2013, 2014 Ken Farmer
"""

# todo:
# 1. validate the validation schema, sigh, well at least a little
# 2. allow users to add args and override config with them
# 3. allow users to lookup environ variables and override config with them

from __future__ import division
import os
import sys

import time
import logging
from pprint import pprint as pp

import yaml
import validictory as valid
import appdirs


class NullHandler(logging.Handler):
    def emit(self, record):
        #print record
        pass


def dcoaler(dict, key, value_default=None):
    """ Coalescing function for dictionaries:
        input arguments:
           - config - dictionary
           - key    - key within dictionary
        output:
           - value associated with key if it exists
             value_default otherwise
        The objective of this function is to provide a very concise way to handle optional
	keys in places like config files.
    """
    try:
        return dict[key]
    except KeyError:
        return value_default





class ConfigManager(object):

    def __init__(self,
                 config_schema=None,
                 log_name='__main__',
                 namespace_access=True):

        self.namespace_access = namespace_access

        # set up logging:
        self.logger   = logging.getLogger('%s.cletus_config' % log_name)
        # don't print to sys.stderr if no parent logger has been set up:
        # logging.getLogger(log_name).addHandler(logging.NullHandler())
        self.logger.debug('ConfigManager starting now')

        self.config_schema = config_schema

        self.config_file      = {}
        self.config_env       = {}
        self.config_namespace = {}
        self.config_dict      = {}
        self.config           = {}

        # store an original copy of variable names to use to protect
        # from updating by bunch later on.
        self.orig_dict_keys   = self.__dict__.keys()

        
    def _bunch(self):
        #self.__dict__.update(adict)
        for key, val in self.config.items():
            if key in self.orig_dict_keys:
                raise ValueError, 'config key is a reserved value: %s' % key
            elif key in dir(ConfigManager):
                raise ValueError, 'config key is a reserved value: %s' % key
            else:
                self.__dict__[key] = val

    def _post_add_maintenance(self, config):
        self.config.update(config)
        self.log_level = dcoaler(self.config, 'log_level', None)
        if self.namespace_access:
           n = self._bunch()



    def add_file(self,
                 app_name=None,
                 config_dir=None,
                 config_fn=None,
                 config_fqfn=None):

        # figure out the config_fqfn:
        if config_fqfn:
            self.config_fqfn = config_fqfn
            self.logger.debug('using config_fqn: %s' % config_fqfn)
        elif config_dir and config_fn:
            self.config_fqfn = os.path.join(config_dir, config_fn)
            self.logger.debug('using config_dir & config_fn: %s' % config_fqfn)
        elif app_name and config_fn:
            self.config_fqfn = os.path.join(appdirs.user_config_dir(app_name), config_fn)
            self.logger.debug('using app_name & config_fn: %s' % config_fqfn)
        else:
            self.logger.critical('Invalid combination of args.  Provide either config_fqfn, config_dir + config_fn, or app_name + config_fn')
            raise ValueError, 'invalid config args'

        if not os.path.isfile(self.config_fqfn):
            self.logger.critical('config file missing: %s' % self.config_fqfn)
            raise IOError, 'config file missing, was expecting %s' % self.config_fqfn

        with open(self.config_fqfn, 'r') as f:
            self.config_file = yaml.safe_load(f)

        self._post_add_maintenance(self.config_file)



    def add_env_vars(self, var_list=None, key_to_lower=False):
        assert key_to_lower in [True, False]

        if var_list:
            my_var_list = var_list
        else:
            if not self.config_schema:
                raise ValueError, 'add_env_vars called without var_list or prior config_schema'
            else:
                my_var_list = self._get_schema_keys()

        mylist = os.environ.items()

        for var_tup in mylist:
            if var_tup[0] in my_var_list:
                if key_to_lower:
                    self.config_env[var_tup[0].lower()] = var_tup[1]
                else:
                    self.config_env[var_tup[0]] = var_tup[1]

        self._post_add_maintenance(self.config_env)



    def _get_schema_keys(self):
        if self.config_schema:
            keylist = [var.upper() for var in self.config_schema['properties'].keys()]
            return keylist
        else:
            return []


    def add_namespace(self, args):
        self.config_namespace.update(vars(args))
        self._post_add_maintenance(self.config_namespace)



    def add_iterable(self, user_iter):

        self.config_dict.update(user_iter)
        self._post_add_maintenance(self.config_dict)


    def validate(self):

        if self.config_schema:
            try:
                valid.validate(self.config, self.config_schema)
            except valid.FieldValidationError as e:
                self.logger.critical('Config error on field %s' % e.fieldname)
                self.logger.critical(e)
                raise ValueError, 'config error: %s' % e
            else:
                return True
        else:
            return None


