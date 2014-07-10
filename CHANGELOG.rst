v0.1 - 2014-03
==============

-  cletus\_log

   -  initial add

-  cletus\_config

   -  initial add

-  cletus\_supp

   -  initial add

-  cletus\_job

   -  initial add

v0.1.4 - 2014-07
================

-  cletus\_job

   -  changed to use flock exclusively rather than the pid from the
      pidfile and a check to see if that pid was still being used. This
      eliminates a big race condition.
   -  added concurrency testing

-  cletus\_config

   -  added namespace, dictionary and env config inputs
   -  added namespace
   -  added test harness

