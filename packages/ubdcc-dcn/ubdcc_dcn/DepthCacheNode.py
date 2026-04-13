#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ¯\_(ツ)_/¯
#
# File: packages/ubdcc-dcn/ubdcc_dcn/DepthCacheNode.py
#
# Project website: https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance
# Github: https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance
# Documentation: https://oliver-zehentleitner.github.io/unicorn-depthcache-cluster-for-binance
# PyPI: https://pypi.org/project/ubdcc-dcn
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
from unicorn_binance_local_depth_cache import BinanceLocalDepthCacheManager, DepthCacheNotFound
from unicorn_binance_local_depth_cache.manager import __version__ as ubldc_version


class DepthCacheNode(ServiceBase):
    def __init__(self, cwd=None):
        super().__init__(app_name="ubdcc-dcn", cwd=cwd)

    async def main(self):
        self.app.data['depthcache_instances'] = {}
        self.app.data['local_depthcaches'] = []
        self.app.data['responsibilities'] = []
        await self.start_rest_server(endpoints=RestEndpoints)
        self.app.set_status_running()
        await self.app.register_or_restart(ubldc_version=ubldc_version)
        self.db_init()
        while self.app.is_shutdown() is False:
            await self.app.sleep()
            await self.app.ubdcc_node_sync()
            self.app.data['responsibilities'] = self.db.get_dcn_responsibilities()
            self.app.stdout_msg(f"Local DepthCaches: {self.app.data['local_depthcaches']}", log="debug", stdout=False)
            self.app.stdout_msg(f"Responsibilities: {self.app.data['responsibilities']}", log="debug", stdout=False)
            for dc in self.app.data['responsibilities']:
                if self.app.is_shutdown() is True:
                    break
                if dc not in self.app.data['local_depthcaches']:
                    # Create DC
                    self.app.stdout_msg(f"Adding local DC: {dc}", log="info")
                    if self.app.data['depthcache_instances'].get(dc['exchange']) is None:
                        self.app.data['depthcache_instances'][dc['exchange']] = {}
                    if self.app.data['depthcache_instances'][dc['exchange']].get(dc['update_interval']) is None:
                        if dc['update_interval'] is None:
                            self.app.data['depthcache_instances'][dc['exchange']][dc['update_interval']] = \
                                BinanceLocalDepthCacheManager(exchange=dc['exchange'])
                        else:
                            self.app.data['depthcache_instances'][dc['exchange']][dc['update_interval']] = \
                                BinanceLocalDepthCacheManager(
                                    exchange=dc['exchange'],
                                    depth_cache_update_interval=dc['update_interval']
                                )
                    else:
                        self.app.data['depthcache_instances'][dc['exchange']][dc['update_interval']].create_depthcache(
                            markets=dc['market'],
                            refresh_interval=dc['refresh_interval']
                        )
                        await self.app.ubdcc_update_depthcache_distribution(exchange=dc['exchange'],
                                                                            market=dc['market'],
                                                                            status="running")
                        self.app.data['local_depthcaches'].append(dc)
                    await self.app.ubdcc_node_sync()
            stop_depthcaches = {}
            for dc in self.app.data['local_depthcaches']:
                if self.app.is_shutdown() is True:
                    break
                if dc not in self.app.data['responsibilities']:
                    # Stop DC
                    self.app.stdout_msg(f"Removing local DC: {dc}", log="info")
                    if stop_depthcaches.get(dc['exchange']) is None:
                        stop_depthcaches[dc['exchange']] = {dc['update_interval']: {'markets': [dc['market']]}}
                    else:
                        if stop_depthcaches[dc['exchange']].get(dc['update_interval']) is None:
                            stop_depthcaches[dc['exchange']] = {dc['update_interval']: {'markets': [dc['market']]}}
                        else:
                            stop_depthcaches[dc['exchange']][dc['update_interval']]['markets'].append(dc['market'])
                    self.app.data['local_depthcaches'].remove(dc)
            for exchange in stop_depthcaches:
                for update_interval in stop_depthcaches[exchange]:
                    try:
                        self.app.data['depthcache_instances'][exchange][update_interval].stop_depthcache(
                            markets=stop_depthcaches[exchange][update_interval]['markets']
                        )
                    except DepthCacheNotFound as error_msg:
                        self.app.stdout_msg(f"DepthCache not found: {error_msg}", log="error")
        self.app.stdout_msg(f"Stopping all DepthCache instances ...", log="error")
        for dc in self.app.data['local_depthcaches']:
            for update_interval in self.app.data['depthcache_instances'][dc['exchange']]:
                self.app.data['depthcache_instances'][dc['exchange']][update_interval].stop_manager()
