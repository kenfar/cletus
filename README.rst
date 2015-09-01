Cletus is a library to help with write commmand line python programs.

It includes: - cletus\_config: makes it easy for a program to combine
config files, environmental variables, and arguments into a single
schema-validated config. - cletus\_supp: allows programs and users to
"suppress" actions with a program simply by touching a file in a
dedicated directory. The suppression action may be to quit, or to simply
sleep or temporarily suspend processing. - cletus\_log: just boilerplate
for common logging. - cletus\_job: a well-tested mechanism that uses a
pid file to ensure that the same file doesn't get run twice.

More info is on the cletus wiki here:
https://github.com/kenfar/cletus/wiki

Installation
============

-  Using `pip <http://www.pip-installer.org/en/latest/>`__ (preferred)
   or
   `easyinstall <http://peak.telecommunity.com/DevCenter/EasyInstall>`__:

   :sub:`~` $ pip install cletus $ easy\_install cletus :sub:`~`

-  Or install manually from
   `pypi <https://pypi.python.org/pypi/cletus>`__:

   :sub:`~` $ mkdir ~$ wget
   https://pypi.python.org/packages/source/d/cletus/cletus-0.1.tar.gz $
   tar -xvf easy\_install cletus $ cd ~-\* $ python setup.py install
   :sub:`~`

Dependencies
============

-  Python 2.7

Licensing
=========

-  Cletus uses the BSD license - see the separate LICENSE file for
   further information

Copyright
=========

-  Copyright 2013, 2014 Ken Farmer
