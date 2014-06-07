#!/usr/bin/env python
""" Used to quickly and easily set up somewhat comprehensive logging.

    Cletus_log is highly opinionated about what constitutes good logging:
       - Logs must be formatted with date, module name, level and msg
         so they can be sorted, searched, or reported on.
       - Logs should be written to a local file system, and should be
         automatically rotated to avoid filling the file system.
       - Logs should be written to the console as well for easy
         interactive debugging.
       - Logs should be trivial to set up, have intelligent defaults,
         be easy to maintain consistency across multiple programs,
         and expose as little logging jargon as possible.

    Anything else is a distraction, is insufficient, or is a (possibly
    totally legimitate) edge case.

    So cletus_log's objective is to make it very easy for most apps to
    provide good logging.

    See the file "LICENSE" for the full license governing use of this file.
    Copyright 2013, 2014 Ken Farmer
"""

from __future__ import division

import os
import sys
import logging
import logging.handlers
import errno
import appdirs


class LogManager(object):

    def __init__(self,
                 log_dir,
                 log_fn,
                 name,
                 log_file_size=100000,
                 log_count=10,
                 log_to_console=True,
                 log_to_file=True):

        self.name           = name
        self.formatter      = None
        self.log_adapter    = None
        self.logger         = logging.getLogger(name)
        self.log_dir        = log_dir
        self.log_fn         = log_fn
        self.log_count      = log_count
        self.log_file_size  = log_file_size

        self._create_log_formatter()

        if log_to_file:
            self._create_file_handler()

        if log_to_console:
            self._create_console_handler()

        # Ensure all crashes get logged:
        sys.excepthook = self._excepthook



    def get_logger(self, initial_msg='Logger starting'):
        """ Creates log adapter
        """
        self.log_adapter = logging.LoggerAdapter(self.logger, {})
        self.log_adapter.info(initial_msg)
        my_logger        = self.log_adapter
        return self.log_adapter



    def _create_log_formatter(self):
        """ Creates a formatter to ensure all records get the following format:
                <ascii time> : <name> : <level name> : <message>
            where
                <ascii time> - has a format of yyyy-mm-dd hh24:mm:ss
                <name>       - is the given module name
                <level name> - is one of DEBUG, INFO, WARNING, ERROR, CRITICAL
                <message>    - is whatever the user provided.
        """
        log_format      = '%(asctime)s : %(name)-12s : %(levelname)-8s : %(message)s'
        date_format     = '%Y-%m-%d %H.%M.%S'
        self.formatter  = logging.Formatter(log_format, date_format)



    def _create_console_handler(self):
        """ Adds a handler to send logs to the console (stdout).
        """
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)



    def _create_file_handler(self):
        """ Adds a handler to send logs to a file.  This is a rotating file handler,
            so when files reach log_file_size they will get renamed and have a numeric
            suffix added.

            If no log_directory was provided then it will get that from the XDG standard
            for user_log_dir.   This is typically $HOME/.cache/name on linux.

            It will attempt to make this directory if it does not exist.
        """
        if self.log_dir is None:
            log_dir    = appdirs.user_log_dir(self.name)

        try:
            os.makedirs(log_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                self.logger.critical('Log directory creation failed.  Log dir: %s' % log_dir)
                raise

        log_fqfn = os.path.join(log_dir, self.log_fn)

        file_handler = logging.handlers.RotatingFileHandler(log_fqfn,
                                                            maxBytes=self.log_file_size,
                                                            backupCount=self.log_count)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)



    def _excepthook(self, *args):
        """ Capture uncaught exceptions, write details into logger, exit.
        """
        self.log_adapter.critical('Uncaught exception - exiting now. ',
                                  exc_info=args)
        sys.exit(1)



def translate_loglevel(loglevel):
    log_translation = {'0':'NOTSET', '10':'DEBUG', '20':'INFO',
                       '30':'WARNING', '40':'ERROR', '50':'CRITICAL',
                       'NOTSET':'0', 'DEBUG':'10', 'INFO':'20',
                       'WARNING':'30', 'ERROR':'40', 'CRITICAL':'50'}
    #self.logger.setLevel(logging._levelNames[self.conf_loglevel.upper()])
    return log_translation[str(loglevel)]







