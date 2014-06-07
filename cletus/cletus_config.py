#!/usr/bin/env python
""" Used to manage access to config files.

    See the file "LICENSE" for the full license governing use of this file.
    Copyright 2013, 2014 Ken Farmer
"""

from __future__ import division
import os
import sys

import yaml
import time
import logging
from pprint import pprint as pp
import validictory as valid


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
                 config_dir,
                 config_fn,
                 config_schema,
                 log_name='main',
                 additional_properties=False):

        assert additional_properties in (True, False)

        # set up logging:
        self.logger   = logging.getLogger('%s.cletus_config' % log_name)
        # don't print to sys.stderr if no parent logger has been set up:
        # logging.getLogger(log_name).addHandler(logging.NullHandler())
        self.logger.debug('ConfigManager starting now')

        self.additional_properties = additional_properties
        self.config_dir    = config_dir
        self.config_fn     = config_fn
        self.config_fqfn   = os.path.join(self.config_dir, self.config_fn)
        self.config_schema = config_schema

        if not os.path.exists(config_dir):
            self.logger.warning('config dir (%s) is missing - I will create it now' % config_dir)
            os.makedirs(config_dir)
        if not os.path.isfile(self.config_fqfn):
            self.logger.critical('config file missing: %s' % self.config_fqfn)
            self.logger.critical('config file should be at: %s' % self.config_fqfn)
            sys.exit(1)

        with open(self.config_fqfn, 'r') as f:
            self.config    = yaml.safe_load(f)
            self.log_level = dcoaler(self.config, 'log_level', None)

        self._validate()

        # add config to namespace
        # now config items can be access either via dict or namespace
        self.__dict__.update(self.config)



    def _validate(self):

        try:
            valid.validate(self.config, self.config_schema)
        except valid.FieldValidationError as e:
            self.logger.critical('Config error on field %s' % e.fieldname)
            self.logger.critical(e)
            sys.exit(1)

        if self.log_level:
            if self.log_level not in ['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                self.logger.critical('config parsing error for %s' % self.config_fqfn)
                self.logger.critical('    log_level has an invalid value of: %s' % self.log_level)
                self.logger.critical('    should be one of: None, notset, debug, info, warning, error, critical')
                sys.exit(1)






