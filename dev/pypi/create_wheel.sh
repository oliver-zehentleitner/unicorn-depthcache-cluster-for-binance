#!/usr/bin/bash
# -*- coding: utf-8 -*-
#
# File: pypi/create_wheel.sh
#
# Part of ‘UNICORN Binance DepthCache Cluster’
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

#set -xeuo pipefail
#set -xeu pipefail

security-check() {
    echo -n "Did you change the version in \`CHANGELOG.md\` and used \`dev/set_version.py\`? [yes|NO] "
    local SURE
    read SURE
    if [ "$SURE" != "yes" ]; then
        exit 1
    fi
}

compile() {
    echo "ok, lets go ..."
    python3 setup.py bdist_wheel sdist
}

security-check
compile
