#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# File: pypi/remove_files.sh
#
# Part of ‘UNICORN Binance WebSocket API’
# Project website: https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance
# Github: https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance
# Documentation: https://oliver-zehentleitner.github.io/unicorn-depthcache-cluster-for-binance
# PyPI: https://pypi.org/project/unicorn-depthcache-cluster-for-binance
# LUCIT Online Shop: https://github.com/oliver-zehentleitner
#
# License: MIT
# https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance/blob/master/LICENSE
#
# Author: Oliver Zehentleitner
#
# Copyright (c) 2019-2024, Oliver Zehentleitner (https://about.me/oliver-zehentleitner)
# All rights reserved.

set -xuo

rm ./build -r
rm ./dist -r
rm ./wheelhouse -r
rm ./*.egg-info -r

rm ubdcc_mgmt/*.so
rm ubdcc_mgmt/*.c
rm ubdcc_shared_modules/*.so
rm ubdcc_shared_modules/*.c
