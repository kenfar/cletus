#!/usr/bin/env python

import os
from setuptools import setup, find_packages

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

version          = "1.0.7"
DESCRIPTION      = 'A library of command line utilities'

setup(name             = 'cletus'     ,
      version          = version           ,
      description      = DESCRIPTION       ,
      long_description=(read('README.rst') + '\n\n' +
                        read('CHANGELOG.rst')),
      keywords         = "utility",
      author           = 'Ken Farmer'      ,
      author_email     = 'kenfar@gmail.com',
      url              = 'http://github.com/kenfar/cletus',
      license          = 'BSD'             ,
      classifiers=[
            'Development Status :: 4 - Beta'                         ,
            'Environment :: Console'                                 ,
            'Intended Audience :: Developers'                        ,
            'License :: OSI Approved :: BSD License'                 ,
            'Programming Language :: Python'                         ,
            'Operating System :: POSIX'                              ,
            'Topic :: Utilities'
            ],
      data_files   = [('/tmp', ['example/cletus_archiver_config.yml'])],
      scripts      = ['scripts/cletus_archiver.py'],
      install_requires     = ['appdirs     == 1.3.0' ,
                              'envoy       == 0.0.2' ,
                              'tox         == 1.7.1' ,
                              'validictory == 0.9.3' ,
                              'pyyaml      == 3.11'  ,
                              'pytest      == 2.6.4' ],
      packages     = find_packages(),
     )
