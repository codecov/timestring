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

import distutils.core
import sys
# Importing setuptools adds some features like "setup.py develop", but
# it's optional so swallow the error if it's not there.
try:
    import setuptools
except ImportError:
    pass

kwargs = {}
version = "0.1b"

distutils.core.setup(
    name="daterange",
    version=version,
    packages = ["daterange"],
    package_data = {},
    author="Steve Peak @stevepeak23",
    author_email="steve@stevepeak.net",
    url="http://stevepeak.github.com/",
    download_url="https://github.com/stevepeak/daterange/archive/master.zip",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="A handler for dates and time ranges that can parse string arguments into date objects.",
    **kwargs
)