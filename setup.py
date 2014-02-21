#!/usr/bin/env python

from setuptools import setup

setup(
    name='Leonardo',
    version='1.0',
    long_description="A Graphite Dashboard, massively inspired by the excellent GDash made by ripienaar",
    packages=["leonardo"],
    include_package_data=True,
    zip_safe=False,
    install_requires=["pyyaml", "flask"]
)

