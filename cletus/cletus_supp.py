#!/usr/bin/env python
""" Used to suppress or block a regularly-scheduled job from running.

    See the file "LICENSE" for the full license governing use of this file.
    Copyright 2013, 2014 Ken Farmer
"""


import os
import errno
import glob
import logging

import appdirs



class NullHandler(logging.Handler):
    def emit(self, record):
        #print record
        pass


class SuppressCheck(object):
    """ Typical Usage:
           supp_check = mod.SuppressCheck(pgm_name)
           if supp_check.suppressed():
               print 'WARNING: filemover has been suppressed'
               sys.exit(0)
    """

    def __init__(self,
                 mnemonic,
                 config_dir=None,
                 log_name='main'):
        """ Does 99% of the work.
        """
        # set up logging
        self.logger   = logging.getLogger('%s.cletus_supp' % log_name)
        # don't print to sys.stderr if no parent logger has been set up:
        #logging.getLogger(log_name).addHandler(logging.NullHandler())
        self.logger.debug('SuppressCheck starting now')

        self.mnemonic        = mnemonic
        if config_dir:
            self.config_dir  = os.path.join(config_dir, 'suppress')
            self.logger.debug('config_dir derrived from arg: %s' % self.config_dir)
        else:
            self.config_dir  = os.path.join(appdirs.user_config_dir(mnemonic), 'suppress')
            self.logger.debug('config_dir provided via user_config_dir: %s' % self.config_dir)

        try:
            os.makedirs(self.config_dir)
            self.logger.info('Suppression dir created successfully')
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                self.logger.critical('Unknown OSError on creating config dir')
                raise

        self.names_suppressed = self._get_suppressed_names()




    def suppressed(self, suppress_name=None):
        """ Determines from suppress_name whether or not that process is
            suppressed.  Returns True/False.
                - if no suppress_name is provided, then the only thing that
                  can suppress it is a file named 'name-all.suppress'.  This
                  typically applies to the main process that is using this
                  class.
                - if a suppress_name is provided, then the only thing that can
                  suppress it is a file named 'name-[suppress_name].suppress'.
        """
        if 'name-all.suppress' in self.names_suppressed:
            self.logger.info('Process has been suppressed')
            return True
        elif suppress_name:
            full_suppress_name = 'name-%s.suppress' % suppress_name
            if full_suppress_name in self.names_suppressed:
                self.logger.info('Process has been suppressed')
                return True
            else:
                return False
        else:
            return False


    def _get_suppressed_names(self):
        raw_files   = glob.glob(os.path.join(self.config_dir, '*.*'))
        clean_files = []
        for one_file in raw_files:
            self.logger.info('checking file: %s' % one_file)
            if _valid_suppress_file(one_file):
                head, tail = os.path.split(one_file)
                clean_files.append(tail)
            else:
                self.logger.critical('invalid suppress file: %s' % one_file)
                raise ValueError
        return clean_files


def _valid_suppress_file(name):
    head, tail = os.path.split(name)
    file_name, file_extension = os.path.splitext(tail)
    if file_extension != '.suppress':
        return False
    elif not file_name.startswith('name-'):
        return False
    else:
        return True




