#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: packages/ubdcc/setup.py
#
# Part of 'UNICORN Binance DepthCache Cluster'
# Project website: https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster
# Github: https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster
# Documentation: https://oliver-zehentleitner.github.io/unicorn-binance-depth-cache-cluster
# PyPI: https://pypi.org/project/ubdcc
#
# License: MIT
# https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/blob/master/LICENSE
#
# Author: Oliver Zehentleitner
#
# Copyright (c) 2024-2026, Oliver Zehentleitner (https://about.me/oliver-zehentleitner)
# All rights reserved.

from setuptools import setup, find_packages

name = "ubdcc"

with open("README.md", "r") as fh:
    print("Using README.md content as `long_description` ...")
    long_description = fh.read()

setup(
    name=name,
    version="0.2.0",
    author="Oliver Zehentleitner",
    author_email='',
    url="https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster",
    description="UNICORN Binance DepthCache Cluster — cluster manager and meta-package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    install_requires=['ubdcc-mgmt',
                      'ubdcc-restapi',
                      'ubdcc-dcn'],
    entry_points={
        "console_scripts": [
            "ubdcc=ubdcc.cli:main",
        ]
    },
    keywords='binance, depth cache, cluster, order book',
    project_urls={
        'Howto': 'https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster#howto',
        'Documentation': 'https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster',
        'Wiki': 'https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/wiki',
        'Author': 'https://www.linkedin.com/in/oliver-zehentleitner',
        'Changes': 'https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/blob/master/packages/ubdcc/CHANGELOG.md',
        'License': 'https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/blob/master/LICENSE',
        'Issue Tracker': 'https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/issues',
        'Telegram': 'https://t.me/unicorndevs',
    },
    python_requires='>=3.9.0',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
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
