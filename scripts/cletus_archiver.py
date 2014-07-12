#!/usr/bin/env  python


import sys
import glob
import os
import time
import argparse

import envoy

# only here to allow running out of dev
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cletus.cletus_log    as log
import cletus.cletus_job    as job
import cletus.cletus_supp   as supp
import cletus.cletus_config as conf


logger    = None
MAX_FILES = 55
APP_NAME  = 'cletus_example'



def main():

    # initialization
    args       = get_args()
    setup_logging(args.log_to_console, args.log_level)
    logger.info('cletus_archiver - starting')
    config     = setup_config(args)
    logger.setLevel(config.log_level or 'DEBUG')
    jobcheck   = check_if_already_running()
    check_if_suppressed()

    # run the process:
    process_all_the_files()

    # housekeeping
    jobcheck.close()
    logger.info('cletus_archiver - terminating normally')
    return 0



def process_all_the_files():

    file_compressor = FileCompressor()

    for i, fn in enumerate(glob.glob('/tmp/*')):

        if i > MAX_FILES:
            logger.warning('max files exceeded - stopping now')
            break

        file_time_epoch, file_time_string = get_file_times(fn)

        if (time.time() - file_time_epoch) > (86400 * 3):

            if fn.endswith('.gz'):
                action = 'skipped'
            elif not os.path.isfile(fn):
                action = 'skipped'
            else:
                file_compressor.compress(fn)
                action = 'compressed'

        else:
            action = 'good'

        logger.debug('%-20.20s - %s - %s' % (abbreviate(fn), file_time_string, action))



class FileCompressor(object):

    def __init__(self):
        logger.debug('cletus_archiver_lib starting')

    def compress(self, fn):
        cmd   = '''gzip %s''' % fn
        r     = envoy.run(cmd)
        if r.status_code:
            logger.error('%s compression failed with status %d' % (fn, r.status_code))
        else:
            logger.debug('%s compressed' % fn)



def abbreviate(fn):
    if len(fn) > 37:
        abbrev_fn = '%s.....' % fn[:37]
        logger.debug('filename truncated: %s' % abbrev_fn)
        return abbrev_fn
    else:
        return fn


def get_file_times(file_name):
    time_epoch  = os.path.getatime(file_name)
    time_string = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.gmtime(time_epoch))
    return time_epoch, time_string



def setup_logging(log_to_console, log_level):
    global logger
    cl_logger  = log.LogManager(app_name=APP_NAME,
                                log_name=__name__,
                                log_to_console=log_to_console)
    logger     = cl_logger.logger
    logger.setLevel(log_level or 'DEBUG')



def setup_config(args):

    config_schema = {'type': 'object',
                     'properties': {
                       'dir':       {'required': True,
                                     'type':     'string'},
                       'log_level': {'enum': ['DEBUG','INFO','WARNING','ERROR','CRITICAL']} ,
                       'config_fqfn': {'required': False,
                                       'type':     'string'},
                       'log_to_console': {'required': False,
                                          'type':     'boolean'} },
                     'additionalProperties': False
                    }
    config = conf.ConfigManager(config_schema)
    config.add_file(app_name=APP_NAME,
                    config_fqfn=args.config_fqfn,
                    config_fn='main.yml')
    config.add_namespace(args)
    config.validate()
    return config




def check_if_already_running():

    jobcheck  = job.JobCheck(app_name=APP_NAME)
    if jobcheck.lock_pidfile():
        logger.info('JobCheck has passed')
        return jobcheck
    else:
        logger.warning('Pgm is already running - this instance will be terminated')
        sys.exit(0)



def check_if_suppressed():

    suppcheck  = supp.SuppressCheck(app_name=APP_NAME)
    if suppcheck.suppressed(suppress_name=APP_NAME):
        logger.warning('Pgm has been suppressed - this instance will be terminated.')
        sys.exit(0)
    else:
        logger.info('SuppCheck has passed')




def get_args():

    usage  = """Cletus sample command-line application that demonstrates
                how to use the cletus libraries.

                This application will compress old files.
             """
    parser = argparse.ArgumentParser(description=usage)

    parser.add_argument('--log-level',
                        choices=['debug','info','warning','error', 'critical'])
    parser.add_argument('--config-fqfn')
    parser.add_argument('--console-log',
                        action='store_true',
                        default=True,
                        dest='log_to_console')
    parser.add_argument('--no-console-log',
                        action='store_false',
                        dest='log_to_console')
    args = parser.parse_args()

    return args



if __name__ == '__main__':
    sys.exit(main())


