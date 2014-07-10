# v0.1 - 2014-03

   * cletus_log
     - initial add

   * cletus_config
     - initial add

   * cletus_supp
     - initial add

   * cletus_job
     - initial add

# v0.1.4 - 2014-07

   * cletus_job
     - changed to use flock exclusively rather than the pid from the pidfile
       and a check to see if that pid was still being used.  This eliminates
       a big race condition.
     - added concurrency testing
   * cletus_config
     - added namespace, dictionary and env config inputs
     - added namespace
     - added test harness
