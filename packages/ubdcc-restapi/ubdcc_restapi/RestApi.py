#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ¯\_(ツ)_/¯
#
# File: packages/ubdcc-restapi/ubdcc_restapi/RestApi.py
#
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

from .RestEndpoints import RestEndpoints
from ubdcc_shared_modules.ServiceBase import ServiceBase


class RestApi(ServiceBase):
    def __init__(self, cwd=None):
        super().__init__(app_name="ubdcc-restapi", cwd=cwd)

    async def main(self):
        await self.start_rest_server(endpoints=RestEndpoints)
        self.app.set_status_running()
        await self.app.register_or_restart()
        self.db_init()
        while self.app.is_shutdown() is False:
            await self.app.sleep()
            await self.app.ubdcc_node_sync()
