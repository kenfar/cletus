# v1.0.13 - 2016-05
   * all
     - add: minor changes tox.ini to support python 2.7, 3.4, 3.5, and pypy

# v1.0.12 - 2015-09
   * cletus_supp.py
     - add: silent arg to SuppressCheck() class to suppress all logging.
       Needed to handle logging volume when continually-checking for
       suppressions.

# v1.0.11 - 2015-05
   * cletus_config.py
     - fix: improved defaulting
   * everything:
     - ran modernizer to make the code more python3-ready

# v1.0.10 - 2015-03
   * cletus_config.py
     - fix: diminished logging

# v1.0.8 - 2015-01
   * cletus_config.py
     - added tests to confirm optional column NULLs
     - added remove_null_overrides to simplify use
     - added apply_defaults to simplify use
     - fix: stopped putting copy of sample configs in /tmp

# v1.0.6 - 2014-07
   * cletus_archiver.py
     - added comments
     - added config to setup

# v1.0.5 - 2014-07

   * cletus_archiver.py
     - moved to script dir from example
     - setup changed to include archiver & config file
   * cletus_supp.py
     - check suppressions directory only when the suppressions method is called,
       so it can be called repeatedly at checkpoints by an app.
     - changed suppressions method behavior to default app_name to init app_name.


# v1.0.4 - 2014-07

   * cletus_job
     - changed to use flock exclusively rather than the pid from the pidfile
       and a check to see if that pid was still being used.  This eliminates
       a big race condition.
     - added concurrency testing
   * cletus_config
     - added namespace, dictionary and env config inputs
     - added namespace
     - added test harness

# v1.0.1 - 2014-03

   * cletus_log
     - initial add

   * cletus_config
     - initial add

   * cletus_supp
     - initial add

   * cletus_job
     - initial add


