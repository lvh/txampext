#!/usr/bin/env python
from setuptools import find_packages, setup

import re
versionLine = open("txampext/_version.py", "rt").read()
match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", versionLine, re.M)
versionString = match.group(1)

setup(name='txampext',
      version=versionString,
      description="Extensions to Twisted's AMP implementation",
      url='https://github.com/lvh/txampext',

      author='Laurens Van Houtven',
      author_email='_@lvh.io',

      packages=find_packages(),

      install_requires=['twisted'],

      license='ISC',
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Twisted",
        "License :: OSI Approved :: ISC License (ISCL)",
        ]
)
