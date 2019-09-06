#! /usr/bin/env python3
"""Energy Tools for Energy Star and ErP Lot 3"""
#
# Copyright (C) 2014-2019 Canonical Ltd.
# Author: Shih-Yuan Lee (FourDollars) <sylee@canonical.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup

__version__ = '1.6.2'

setup(name='energy-tools',
      version=__version__,
      description='Energy Tools for Energy Star 5/6/7/8 and ErP Lot 3',
      long_description='''
This program is designed to collect the system profile and calculate
the results of Energy Star (5.2 & 6.0 & 7.0 & 8.0) and
ErP Lot 3 (Jul. 2014 & Jan. 2016).''',
      platforms=['Linux'],
      license='GPLv3',
      author='Shih-Yuan Lee (FourDollars)',
      author_email='sylee@canonical.com',
      url='https://github.com/fourdollars/energy-tools',
      packages=['energy_tools'],
      scripts=['bin/energy-tools'],
      )
