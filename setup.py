#!/usr/bin/env python3

try:
	from setuptools import setup
except ImportError:
	from distribute_setup import use_setuptools
	use_setuptools()
	from setuptools import setup

setup(setup_requires=['d2to1'], d2to1=True)