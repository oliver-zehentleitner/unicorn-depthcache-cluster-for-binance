#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ¯\_(ツ)_/¯
#
# File: packages/ubdcc-shared-modules/ubdcc_shared_modules/ServiceBase.py
#
# Project website: https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance
# Github: https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance
# Documentation: https://oliver-zehentleitner.github.io/unicorn-depthcache-cluster-for-binance
# PyPI: https://pypi.org/project/ubdcc-shared-modules
#
# License: MIT
# https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance/blob/master/LICENSE
#
# Author: Oliver Zehentleitner
#
# Copyright (c) 2024-2026, Oliver Zehentleitner (https://about.me/oliver-zehentleitner)
# All rights reserved.

import asyncio
import socket
from .App import App
from .RestServer import RestServer
from .Database import Database


class ServiceBase:
    def __init__(self, app_name=None, cwd=None):
        self.db: Database | None = None
        self.rest_server = None
        self.app = App(app_name=app_name,
                       cwd=cwd,
                       service=self,
                       service_call=self.run,
                       stop_call=self.stop)
        self.app.start()
        # Never gets executed ;)

    def db_init(self) -> bool:
        self.app.stdout_msg(f"Starting Database ...", log="info")
        if self.db is None:
            self.db = Database(app=self.app)
            return True
        return False

    @staticmethod
    def is_port_free(port, host='127.0.0.1'):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return True
            except OSError:
                return False

    async def main(self) -> None:
        # Override with specific Service main() function
        pass

    def run(self) -> None:
        self.app.stdout_msg(f"Starting the main execution flow ...", log="debug", stdout=False)
        asyncio.run(self.main())

    async def start_rest_server(self, endpoints=None) -> bool:
        while self.is_port_free(port=self.app.api_port_rest) is False:
            self.app.api_port_rest = self.app.api_port_rest + 1
        self.rest_server = RestServer(app=self.app, endpoints=endpoints, port=self.app.api_port_rest)
        self.rest_server.start()
        await asyncio.sleep(1)
        return True

    def stop(self) -> bool:
        try:
            if self.rest_server:
                self.rest_server.stop()
            return True
        except AttributeError as error_msg:
            self.app.stdout_msg(f"ERROR: {error_msg}", log="info")
        return False
