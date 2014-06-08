#!/usr/bin/env python
""" Used to manage access to config files.

    Cletus_config is highly opinionated about what constitutes good config
    management:
       - Config files should be kept within the xdg directory:
            - linux:  $HOME/.config/<app name>
       - But overrides to the location, for special runs, migrations,
         testing, etc is occasionally necessary.
       - The best format at present for config files is yaml.
       - Config items should be validated.
       - Arguments should override config items.
       - It's easier to reference config items as namespaces than
         dictionaries.

    The objective of cletus_config is to deliver on this optinions in a way
    that makes it easy for applications.

    See the file "LICENSE" for the full license governing use of this file.
    Copyright 2013, 2014 Ken Farmer
"""

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
                 app_name=None,
                 config_dir=None,
                 config_fn=None,
                 config_fqfn=None,
                 config_schema=None,
                 log_name='__main__',
                 additional_properties=False):


        # set up logging:
        self.logger   = logging.getLogger('%s.cletus_config' % log_name)
        # don't print to sys.stderr if no parent logger has been set up:
        # logging.getLogger(log_name).addHandler(logging.NullHandler())
        self.logger.debug('ConfigManager starting now')

        assert additional_properties in (True, False)
        self.additional_properties = additional_properties

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

        self.config_schema = config_schema

        if not os.path.isfile(self.config_fqfn):
            self.logger.critical('config file missing: %s' % self.config_fqfn)
            raise IOError, 'config file missing, was expecting %s' % self.config_fqfn

        with open(self.config_fqfn, 'r') as f:
            self.config    = yaml.safe_load(f)
            self.log_level = dcoaler(self.config, 'log_level', None)

        if self.config_schema:
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






