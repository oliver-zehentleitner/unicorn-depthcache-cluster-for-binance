#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ¯\_(ツ)_/¯
#
# File: packages/ubdcc-dcn/ubdcc_dcn/DepthCacheNode.py
#
# Project website: https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster
# Github: https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster
# Documentation: https://oliver-zehentleitner.github.io/unicorn-binance-depth-cache-cluster
# PyPI: https://pypi.org/project/ubdcc-dcn
#
# License: MIT
# https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/blob/master/LICENSE
#
# Author: Oliver Zehentleitner
#
# Copyright (c) 2024-2026, Oliver Zehentleitner (https://about.me/oliver-zehentleitner)
# All rights reserved.

import queue
from functools import partial

from .RestEndpoints import RestEndpoints
from ubdcc_shared_modules.AccountGroups import get_account_group
from ubdcc_shared_modules.ServiceBase import ServiceBase
from unicorn_binance_local_depth_cache import BinanceLocalDepthCacheManager, DepthCacheNotFound
from unicorn_binance_local_depth_cache.manager import __version__ as ubldc_version


class DepthCacheNode(ServiceBase):
    def __init__(self, cwd=None, mgmt_port=None, log_level=None):
        # Thread-safe queue: UBLDC on_restart callbacks fire from their
        # manager thread; the async main loop drains the queue and forwards
        # to mgmt. Must be initialized BEFORE super().__init__() because
        # ServiceBase.__init__() calls self.app.start() which blocks and
        # synchronously runs main() → _drain_restart_queue(). Any attribute
        # set after super().__init__() is never assigned.
        self._restart_queue: queue.Queue = queue.Queue()
        super().__init__(app_name="ubdcc-dcn", cwd=cwd, mgmt_port=mgmt_port, log_level=log_level)

    def _on_stream_restart(self, exchange: str, market: str, timestamp: float) -> None:
        """Thread-safe: invoked from UBLDC's manager thread on every stream restart."""
        self._restart_queue.put((exchange, market, timestamp))

    def _ldcs_for_account_group(self, account_group: str):
        """Yield every running BinanceLocalDepthCacheManager whose exchange maps
        to the given account_group."""
        for exchange, by_interval in self.app.data.get('depthcache_instances', {}).items():
            if get_account_group(exchange) != account_group:
                continue
            for ldc in by_interval.values():
                if ldc is not None:
                    yield ldc

    async def _sync_credentials(self) -> None:
        """For every account_group currently used by this DCN, pull the assigned
        credential from mgmt. If the credential id differs from the one we last
        propagated, hot-swap the UBRA in all affected UBLDCs via
        `set_credentials()`. Runs once per main-loop iteration after the
        mgmt sync."""
        cache = self.app.data['credential_id_by_account_group']
        used_account_groups = {get_account_group(exch)
                               for exch in self.app.data.get('depthcache_instances', {})}
        used_account_groups.discard(None)
        for account_group in used_account_groups:
            credential = await self.app.ubdcc_assign_credentials(account_group=account_group)
            new_id = credential.get('id') if credential else None
            if cache.get(account_group) == new_id:
                continue
            api_key = credential.get('api_key') if credential else None
            api_secret = credential.get('api_secret') if credential else None
            for ldc in self._ldcs_for_account_group(account_group):
                try:
                    ldc.set_credentials(api_key=api_key, api_secret=api_secret)
                except Exception as error_msg:
                    self.app.stdout_msg(f"set_credentials() failed for '{account_group}': "
                                        f"{error_msg}", log="error")
            cache[account_group] = new_id
            if new_id is not None:
                self.app.stdout_msg(f"Assigned credential '{new_id}' for account_group "
                                    f"'{account_group}'.", log="info")
            else:
                self.app.stdout_msg(f"No credential available for account_group "
                                    f"'{account_group}' — using public rate limits.",
                                    log="info")

    async def main(self):
        self.app.data['depthcache_instances'] = {}
        self.app.data['local_depthcaches'] = []
        self.app.data['responsibilities'] = []
        self.app.data['credential_id_by_account_group'] = {}
        await self.start_rest_server(endpoints=RestEndpoints)
        self.app.set_status_running()
        await self.app.register_or_restart(ubldc_version=ubldc_version)
        self.db_init()
        while self.app.is_shutdown() is False:
            await self.app.sleep()
            await self.app.ubdcc_node_sync()
            await self._drain_restart_queue()
            await self._sync_credentials()
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
                        on_restart = partial(self._on_stream_restart, dc['exchange'])
                        kwargs = {"exchange": dc['exchange'], "on_restart": on_restart}
                        if dc['update_interval'] is not None:
                            kwargs['depth_cache_update_interval'] = dc['update_interval']
                        # The UBRA is managed by UBLDC itself (no ubra_manager
                        # kwarg); credentials are propagated immediately below
                        # so the initial snapshot already runs with an
                        # authenticated key when one is assigned.
                        self.app.data['depthcache_instances'][dc['exchange']][dc['update_interval']] = \
                            BinanceLocalDepthCacheManager(**kwargs)
                        await self._sync_credentials()
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

    async def _drain_restart_queue(self) -> None:
        """
        Drain pending stream-restart events from UBLDC's on_restart callback
        and forward each one to mgmt. Runs once per main-loop iteration.
        """
        while True:
            try:
                exchange, market, timestamp = self._restart_queue.get_nowait()
            except queue.Empty:
                return
            await self.app.ubdcc_update_depthcache_distribution(
                exchange=exchange,
                market=market,
                last_restart_time=timestamp,
            )
