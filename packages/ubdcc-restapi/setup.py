#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: packages/ubdcc-restapi/setup.py
#
# Part of ‘UNICORN Binance DepthCache Cluster’
# Project website: https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance
# Github: https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance
# Documentation: https://oliver-zehentleitner.github.io/unicorn-depthcache-cluster-for-binance
# PyPI: https://pypi.org/project/ubdcc-restapi
#
# License: MIT
# https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance/blob/master/LICENSE
#
# Author: Oliver Zehentleitner
#
# Copyright (c) 2024-2026, Oliver Zehentleitner (https://about.me/oliver-zehentleitner)
# All rights reserved.

from Cython.Build import cythonize
from setuptools import setup

name = "ubdcc-restapi"
source_dir = "ubdcc_restapi"

# Setup
with open("README.md", "r") as fh:
    print("Using README.md content as `long_description` ...")
    long_description = fh.read()

setup(
    name=name,
    version="0.1.4",
    author="Oliver Zehentleitner",
    author_email='',
    url="https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance",
    description="UBDCC REST API — public REST interface for the UNICORN DepthCache Cluster for Binance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    install_requires=['ubdcc-shared-modules==0.1.4'],
    keywords='',
    project_urls={
        'Howto': 'https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance#howto',
        'Documentation': 'https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance',
        'Wiki': 'https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance/wiki',
        'Author': 'https://about.me/oliver-zehentleitner',
        'Changes': 'https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance/blob/master/packages/ubdcc-restapi/CHANGELOG.md',
        'License': 'https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance/blob/master/LICENSE',
        'Issue Tracker': 'https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance/issues',
        'Chat': 'https://gitter.im/unicorn-trading-suite/unicorn-depthcache-cluster-for-binance',
        'Telegram': 'https://t.me/unicorndevs',
        'Get Support': 'https://about.me/oliver-zehentleitner/get-support.html',
    },
    ext_modules=cythonize(['ubdcc_restapi/__init__.py',
                           'ubdcc_restapi/RestEndpoints.py',
                           'ubdcc_restapi/RestApi.py'],
                          compiler_directives={'language_level': "3"}),
    python_requires='>=3.12.0',
    package_data={'': ['ubdcc_restapi/*.so']},
    exclude_package_data={'': ['ubdcc_restapi/*.py']},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Cython",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: AsyncIO",
    ],
)
