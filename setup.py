#!/usr/bin/env python
from setuptools import setup

setup(name='timestring',
      version='1.4.4',
      description="Human expressed time to Dates and Ranges",
      long_description="""Converting strings of into representable time via Date and Range objects.
 Plus features to compare and adjust Dates and Ranges.""",
      classifiers=["Development Status :: 5 - Production/Stable",
                   "License :: OSI Approved :: Apache Software License",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2.6",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: Implementation :: PyPy"],
      keywords='date time range datetime datestring',
      author='@iopeak',
      author_email='steve@stevepeak.net',
      url='http://github.com/stevepeak/timestring',
      license='http://www.apache.org/licenses/LICENSE-2.0',
      packages=['timestring'],
      include_package_data=True,
      zip_safe=True,
      install_requires=["pytz==2013b"],
      entry_points="")
