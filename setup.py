#!/usr/bin/env python
from setuptools import setup

version = '1.6.0'

setup(name='timestring',
      version=version,
      description="Human expressed time to Dates and Ranges",
      long_description="""Converting strings of into representable time via Date and Range objects.
 Plus features to compare and adjust Dates and Ranges.""",
      classifiers=["Development Status :: 5 - Production/Stable",
                   "License :: OSI Approved :: Apache Software License",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2.6",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.2",
                   "Programming Language :: Python :: 3.3",
                   "Programming Language :: Python :: Implementation :: PyPy"],
      keywords='date time range datetime datestring',
      author='@stevepeak',
      author_email='steve@stevepeak.net',
      url='http://github.com/stevepeak/timestring',
      license='http://www.apache.org/licenses/LICENSE-2.0',
      packages=['timestring'],
      include_package_data=True,
      zip_safe=True,
      install_requires=["pytz==2013b"],
      entry_points={'console_scripts': ['timestring=timestring:main']})
