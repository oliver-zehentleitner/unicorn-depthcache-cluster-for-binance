#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ¯\_(ツ)_/¯
#
# File: packages/ubdcc-shared-modules/ubdcc_shared_modules/AccountGroups.py
#
# Project website: https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster
# Github: https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster
# Documentation: https://oliver-zehentleitner.github.io/unicorn-binance-depth-cache-cluster
# PyPI: https://pypi.org/project/ubdcc-shared-modules
#
# License: MIT
# https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/blob/master/LICENSE
#
# Author: Oliver Zehentleitner
#
# Copyright (c) 2024-2026, Oliver Zehentleitner (https://about.me/oliver-zehentleitner)
# All rights reserved.

# Exchange string (UBLDC) -> account_group. Group = one shared Binance account
# (same login/keys). Spot-testnet and futures-testnet are separate accounts on
# Binance, hence separate groups.
EXCHANGE_TO_ACCOUNT_GROUP = {
    "binance.com": "binance.com",
    "binance.com-futures": "binance.com",
    "binance.com-margin": "binance.com",
    "binance.com-isolated_margin": "binance.com",
    "binance.com-testnet": "binance.com-testnet",
    "binance.com-futures-testnet": "binance.com-futures-testnet",
    "binance.us": "binance.us",
    "trbinance.com": "binance.tr",
}

ACCOUNT_GROUPS = sorted(set(EXCHANGE_TO_ACCOUNT_GROUP.values()))


def get_account_group(exchange: str) -> str | None:
    if exchange is None:
        return None
    return EXCHANGE_TO_ACCOUNT_GROUP.get(exchange)


def is_valid_account_group(account_group: str) -> bool:
    return account_group in ACCOUNT_GROUPS
