#!/usr/bin/env python

from distutils.core import setup

setup(name='python-bitsharesrpc',
      version='0.1',
      description='RPC interface for the BitShares client',
      long_description=open('README').read(),
      author='Fabian Schuh',
      author_email='<mail@xeroc.org>',
      maintainer='Fabian Schuh',
      maintainer_email='<mail@xeroc.org>',
      url='http://www.github.com/xeroc/python-bitsharesrpc',
      packages=['bitsharesrpc'],
      classifiers=['License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)', 'Operating System :: OS Independent'])
