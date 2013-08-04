#!/usr/bin/env python
#
# Copyright 2013 Steve Peak
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from setuptools import setup

version = '1.4.3'

setup(name='timestring',
      version=version,
      description="Human expressed time to Dates and Ranges",
      long_description="""Converting strings of into representable time via Date and Range objects.
 Plus features to compare and adjust Dates and Ranges.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='date time range datetime datestring',
      author='Steve Peak @iopeak',
      author_email='steve@stevepeak.net',
      url='http://github.com/stevepeak/timestring',
      license='http://www.apache.org/licenses/LICENSE-2.0',
      packages = ['timestring'],
      include_package_data=True,
      zip_safe=True,
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
