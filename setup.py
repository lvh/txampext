#!/usr/bin/env python
from setuptools import find_packages, setup

setup(name='txampext',
      version='20130105',
      description="Extensions to Twisted's AMP implementation",
      url='https://github.com/lvh/txampext',

      author='Laurens Van Houtven',
      author_email='_@lvh.cc',

      packages=find_packages(),

      install_requires=['twisted'],

      license='ISC',
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Twisted",
        "License :: OSI Approved :: ISC License (ISCL)",
        ])

