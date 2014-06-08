#!/usr/bin/env python

import logging
import envoy


class FileCompressor(object):

    def __init__(self, log_name):

        #self.logger = logging.getLogger('__main__.lib')
        #self.logger = logging.getLogger(__name__)
        #self.logger = logging.getLogger()
        #print 'lib name: %s' % __name__
        #print 'all logger names: '
        #print logging.Logger.manager.loggerDict.keys()

        self.logger = logging.getLogger('%s.FileCompressor' % log_name)
        self.logger.debug('cletus_archiver_lib starting')


    def compress(self, fn):
        cmd   = '''gzip %s''' % fn
        r     = envoy.run(cmd)
        if r.status_code:
            self.logger.error('%s compression failed with status %d' % (fn, r.status_code))
        else:
            self.logger.debug('%s compressed' % fn)
