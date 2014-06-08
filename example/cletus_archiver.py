#!/usr/bin/env  python


import sys
import glob
import os
import time
import argparse

import envoy
import appdirs

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cletus.cletus_log    as log
import cletus.cletus_job    as job
import cletus.cletus_supp   as supp
import cletus.cletus_config as conf

import cletus_archiver_lib  as lib

logger    = None
MAX_FILES = 55
APP_NAME  = 'cletus_example'



def main():

    args      = get_args()

    # set up logging:
    setup_logging(args.log_to_console, args.log_level)

    # set up config
    config     = setup_config(args.config)

    # check if already running
    check_if_already_running()

    # run the process:
    process_all_the_files()



def process_all_the_files():

    file_compressor = lib.FileCompressor(__name__)

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

        logger.debug('%-20.20s - %s - %s' % (abbrev_fn(fn), file_time_string, action))


def abbrev_fn(fn):
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
    logger.info('cletus_archiver starting!')



def setup_config(args_config):

    config_schema = {'type': 'object',
                     'properties': {
                       'dir':  {'required': True,
                                'type':     'string'},
                       'log_level': {'enum': ['DEBUG','INFO','WARNING','ERROR','CRITICAL']} },
                     'additionalProperties': False
                    }

    config = conf.ConfigManager(app_name=APP_NAME,
                                config_fqfn=args_config,
                                config_fn='main.yml',
                                config_schema=config_schema,
                                log_name=__name__)
    return config




def check_if_already_running():

    jobcheck  = job.JobCheck(app_name=APP_NAME,
                             log_name=__name__)
    if jobcheck.old_job_age > 0:
        logger.warning('Pgm is already running - this instance will be terminated')
        logger.warning('old job has been running %d seconds' % jobcheck.old_job_age)
        sys.exit(0)
    else:
        logger.info('JobCheck has passed')




def get_args():

    usage  = """Cletus sample command-line application that demonstrates
                how to use the cletus libraries.

                This application will compress old files.
             """
    parser = argparse.ArgumentParser(description=usage)

    parser.add_argument('--log-level',
                        choices=['debug','info','warning','error', 'critical'])

    parser.add_argument('--config')


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


