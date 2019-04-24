#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='Leonardo',
    version='1.0',
    long_description="A Graphite Dashboard, massively inspired by the excellent GDash made by ripienaar",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3.7']
)

