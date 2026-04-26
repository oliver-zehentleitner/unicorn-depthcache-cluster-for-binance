#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ¯\_(ツ)_/¯
#
# File: packages/ubdcc-mgmt/ubdcc_mgmt/Mgmt.py
#
# Project website: https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster
# Github: https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster
# Documentation: https://oliver-zehentleitner.github.io/unicorn-binance-depth-cache-cluster
# PyPI: https://pypi.org/project/ubdcc-mgmt
#
# License: MIT
# https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/blob/master/LICENSE
#
# Author: Oliver Zehentleitner
#
# Copyright (c) 2024-2026, Oliver Zehentleitner (https://about.me/oliver-zehentleitner)
# All rights reserved.

from .RestEndpoints import RestEndpoints
from ubdcc_shared_modules.ServiceBase import ServiceBase


class Mgmt(ServiceBase):
    def __init__(self, cwd=None, mgmt_port=None, log_level=None):
        super().__init__(app_name="ubdcc-mgmt", cwd=cwd, mgmt_port=mgmt_port, log_level=log_level)

    async def main(self):
        self.db_init()
        await self.start_rest_server(endpoints=RestEndpoints)
        await self.app.sleep(seconds=15)
        while self.app.is_shutdown() is False:
            self.db.revise()
            await self.app.sleep(seconds=10)
