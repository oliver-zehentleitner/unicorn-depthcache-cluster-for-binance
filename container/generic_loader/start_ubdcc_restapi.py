#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ¯\_(ツ)_/¯
#
# File: container/generic_loader/start_ubdcc_dcn.py
#
# Project website: https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster
# Github: https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster
# Documentation: https://oliver-zehentleitner.github.io/unicorn-binance-depth-cache-cluster
# PyPI: https://pypi.org/project/unicorn-binance-depth-cache-cluster
# LUCIT Online Shop: https://github.com/oliver-zehentleitner
#
# License: MIT
# https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/blob/master/LICENSE
#
# Author: Oliver Zehentleitner
#
# Copyright (c) 2024-2026, Oliver Zehentleitner (https://about.me/oliver-zehentleitner)
# All rights reserved.

import os
from ubdcc_restapi import RestApi

RestApi.RestApi(cwd=os.path.dirname(os.path.abspath(__file__)))
