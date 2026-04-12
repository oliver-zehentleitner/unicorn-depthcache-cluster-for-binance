#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ¯\_(ツ)_/¯
#
# File: packages/ubdcc-shared-modules/ubdcc_shared_modules/RestServer.py
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

import threading
import uvicorn
from fastapi import HTTPException
from uvicorn.config import LOGGING_CONFIG


class RestServer(threading.Thread):
    def __init__(self, app=None, endpoints=None, port=None):
        super().__init__()
        self.app = app
        self.endpoints = endpoints(app=self.app)
        self.endpoints.register()
        LOGGING_CONFIG["formatters"]["access"]["fmt"] = f"%(asctime)s {LOGGING_CONFIG['formatters']['access']['fmt']}"
        self.app.stdout_msg(f"Registering REST Server on port {port} ...", log="info")
        self.uvicorn = uvicorn.Server(uvicorn.Config(self.app.get_fastapi_instance(),
                                                     host="0.0.0.0",
                                                     port=port))

    def run(self) -> None:
        self.app.stdout_msg(f"Starting REST Server Engine ...", log="info")
        try:
            self.uvicorn.run()
        except (ConnectionError, HTTPException) as error_msg:
            self.app.stdout_msg(f"ERROR: {error_msg}", log="critical")
        return None

    def stop(self) -> bool:
        self.app.stdout_msg(f"Stopping REST Server Engine ...", log="info")
        self.uvicorn.should_exit = True
        return True
