#!/usr/bin/env python
""" Used to quickly and easily set up somewhat comprehensive logging.

    See the file "LICENSE" for the full license governing use of this file.
    Copyright 2013, 2014 Ken Farmer
"""


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
        self.log_adapter    = None
        self.formatter      = None
        self.log_adapter    = None
        self.logger         = logging.getLogger(name)

        self.create_log_formatter()

        if log_to_file:
            self.create_file_handler(self.formatter, log_dir, log_fn,
                                     log_file_size, log_count)

        if log_to_console:
            self.create_console_handler(self.formatter)

        # Ensure all crashes get logged:
        sys.excepthook = self.excepthook


    def create_log_formatter(self):
        log_format      = '%(asctime)s : %(name)-12s : %(levelname)-8s : %(message)s'
        date_format     = '%Y-%m-%d %H.%M.%S'
        self.formatter  = logging.Formatter(log_format, date_format)


    def create_console_handler(self, formatter):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)


    def create_file_handler(self, formatter, log_dir, log_fn, log_file_size, log_count):
        if log_dir is None:
            log_dir    = appdirs.user_data_dir(self.name)
        try:
            os.makedirs(log_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                self.logger.critical('Log directory creation failed.  Log dir: %s' % log_dir)
                raise
        log_fqfn = os.path.join(log_dir, log_fn)

        file_handler = logging.handlers.RotatingFileHandler (log_fqfn,
                                                             maxBytes=log_file_size,
                                                             backupCount=log_count)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)



    def get_logger(self, initial_msg='Logger starting'):
        """ Creates log adapter
            Also create global my_logger reference to it for excepthook.
        """
        self.log_adapter = logging.LoggerAdapter(self.logger, {})
        self.log_adapter.info(initial_msg)
        my_logger        = self.log_adapter
        return self.log_adapter



    def excepthook(self, *args):
        """ Capture uncaught exceptions, write details into logger, exit.
            For future reference, could alternatively make this code reusable
            with following line:
            logging.getLogger().error('Uncaught exception: ', exc_info=args)
        """
        self.log_adapter.critical('Uncaught exception - exiting now. ', exc_info=args)
        sys.exit(100)


def translate_loglevel(loglevel):
    log_translation = {'0':'NOTSET', '10':'DEBUG', '20':'INFO',
                       '30':'WARNING', '40':'ERROR', '50':'CRITICAL',
                       'NOTSET':'0', 'DEBUG':'10', 'INFO':'20',
                       'WARNING':'30', 'ERROR':'40', 'CRITICAL':'50'}
    #self.logger.setLevel(logging._levelNames[self.conf_loglevel.upper()])
    return log_translation[str(loglevel)]







