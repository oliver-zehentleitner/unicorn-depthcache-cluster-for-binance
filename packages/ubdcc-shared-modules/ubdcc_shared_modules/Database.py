#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ¯\_(ツ)_/¯
#
# File: packages/ubdcc-mgmt/ubdcc_mgmt/Database.py
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

import threading
import time
import uuid


class Database:
    def __init__(self, app=None):
        self.app = app
        self.app.data['db'] = self
        self.data = {}
        self.data_lock = threading.Lock()
        self._init()

    def _init(self) -> bool:
        self.app.stdout_msg(f"Initiating Database ...", log="info")
        self.set(key="depthcaches", value={})
        self.set(key="nodes", value={})
        self.set(key="pods", value={})
        self.set(key="credentials", value={})
        self.set(key="timestamp", value=float())
        if self.app.info['name'] == "ubdcc-mgmt":
            self.update_nodes()
        return True

    def _set_update_timestamp(self) -> bool:
        self.data['timestamp'] = self.app.get_unix_timestamp()
        return True

    def is_empty(self) -> bool:
        if len(self.data['pods']) == 0 and \
                len(self.data['depthcaches']) == 0:
            return True
        return False

    def add_depthcache(self,
                       exchange: str = None,
                       market: str = None,
                       desired_quantity: int = None,
                       update_interval: int = None,
                       refresh_interval: int = None) -> bool:
        if exchange is None or market is None:
            raise ValueError("Missing mandatory parameter: exchange, market")
        if desired_quantity is None or desired_quantity == "None":
            desired_quantity = 1
        else:
            desired_quantity = int(desired_quantity)
        if update_interval is None or update_interval == "None":
            update_interval = None
        else:
            update_interval = int(update_interval)
        if refresh_interval is None or refresh_interval == "None":
            refresh_interval = None
        else:
            refresh_interval = int(refresh_interval)
        depthcache = {"CREATED_TIME": self.app.get_unix_timestamp(),
                      "DESIRED_QUANTITY": desired_quantity,
                      "DISTRIBUTION": {},
                      "DISTRIBUTION_CHANGES": 0,
                      "EXCHANGE": exchange,
                      "LAST_DISTRIBUTION_CHANGE": 0,
                      "REFRESH_INTERVAL": refresh_interval,
                      "MARKET": market,
                      "UPDATE_INTERVAL": update_interval}
        with self.data_lock:
            if self.data['depthcaches'].get(exchange) is None:
                self.data['depthcaches'][exchange] = {}
            self.data['depthcaches'][exchange][market] = depthcache
            self._set_update_timestamp()
        return True

    def add_depthcache_distribution(self,
                                    exchange: str = None,
                                    market: str = None,
                                    pod_uid: str = None,
                                    scheduled_start_time: float = None) -> bool:
        if exchange is None or market is None or pod_uid is None or scheduled_start_time is None:
            raise ValueError("Missing mandatory parameter: exchange, pod_uid, market, scheduled_start_time")
        distribution = {"CREATED_TIME": self.app.get_unix_timestamp(),
                        "LAST_RESTART_TIME": 0,
                        "POD_UID": pod_uid,
                        "RESTARTS": 0,
                        "SCHEDULED_START_TIME": scheduled_start_time,
                        "STATUS": "starting"}
        with self.data_lock:
            self.data['depthcaches'][exchange][market]['DISTRIBUTION'][pod_uid] = distribution
            self.data['depthcaches'][exchange][market]['DISTRIBUTION_CHANGES'] = \
                self.data['depthcaches'][exchange][market].get('DISTRIBUTION_CHANGES', 0) + 1
            self.data['depthcaches'][exchange][market]['LAST_DISTRIBUTION_CHANGE'] = \
                self.app.get_unix_timestamp()
            self._set_update_timestamp()
        return True

    def add_pod(self, name: str = None, uid: str = None, node: str = None, role: str = None, ip: str = None,
                api_port_rest: int = None, status: str = None, ubldc_version: str = None, version: str = None) -> bool:
        if uid is None:
            raise ValueError("Missing mandatory parameter: uid")
        pod = {"NAME": name,
               "UID": uid,
               "NODE": node,
               "ROLE": role,
               "IP": ip,
               "API_PORT_REST": api_port_rest,
               "LAST_SEEN": self.app.get_unix_timestamp(),
               "STATUS": status,
               "UBLDC_VERSION": ubldc_version,
               "VERSION": version}
        if ubldc_version is None:
            del pod['UBLDC_VERSION']
        with self.data_lock:
            self.data['pods'][uid] = pod
            self._set_update_timestamp()
        return True

    def add_credentials(self, account_group: str = None, api_key: str = None,
                        api_secret: str = None) -> str:
        """Store a Binance API key pair for the given account group. Returns
        the generated credential id (UUID). Raises ValueError on invalid
        parameters or unknown account_group."""
        if account_group is None or api_key is None or api_secret is None:
            raise ValueError("Missing mandatory parameter: account_group, api_key, api_secret")
        from .AccountGroups import is_valid_account_group
        if not is_valid_account_group(account_group):
            raise ValueError(f"Invalid account_group: {account_group}")
        credential_id = str(uuid.uuid4())
        credential = {"ID": credential_id,
                      "ACCOUNT_GROUP": account_group,
                      "API_KEY": api_key,
                      "API_SECRET": api_secret,
                      "ADDED_TIMESTAMP": self.app.get_unix_timestamp(),
                      "ASSIGNED_DCNS": []}
        with self.data_lock:
            if self.data.get('credentials') is None:
                self.data['credentials'] = {}
            self.data['credentials'][credential_id] = credential
            self._set_update_timestamp()
        return credential_id

    def assign_credentials(self, uid: str = None, account_group: str = None) -> dict | None:
        """Assign (or return already-assigned) credential to a DCN uid.
        Load-balanced: picks credential with fewest ASSIGNED_DCNS.
        Returns full credential dict (incl. secret) or None if no keys available.
        """
        if uid is None or account_group is None:
            raise ValueError("Missing mandatory parameter: uid, account_group")
        with self.data_lock:
            credentials = self.data.get('credentials') or {}
            candidates = [c for c in credentials.values()
                          if c['ACCOUNT_GROUP'] == account_group]
            if not candidates:
                return None
            for c in candidates:
                if uid in c['ASSIGNED_DCNS']:
                    return dict(c)
            chosen = min(candidates, key=lambda c: len(c['ASSIGNED_DCNS']))
            chosen['ASSIGNED_DCNS'].append(uid)
            self._set_update_timestamp()
            return dict(chosen)

    def delete_credentials(self, credential_id: str = None) -> bool:
        """Remove a stored credential. Returns True on success, False when the
        id was not found."""
        if credential_id is None:
            raise ValueError("Missing mandatory parameter: credential_id")
        with self.data_lock:
            credentials = self.data.get('credentials') or {}
            if credential_id not in credentials:
                return False
            del credentials[credential_id]
            self._set_update_timestamp()
        return True

    def get_credentials(self, credential_id: str = None) -> dict | None:
        """Return the full credential record (incl. secret) for the given id,
        or None if not found. Internal use only — do not leak through public
        endpoints."""
        with self.data_lock:
            credentials = self.data.get('credentials') or {}
            c = credentials.get(credential_id)
            return dict(c) if c else None

    def get_credentials_list(self, reveal_secrets: bool = False) -> list:
        """Return list of credentials. With reveal_secrets=False (default)
        api_key/api_secret are masked for public consumption."""
        result = []
        with self.data_lock:
            credentials = self.data.get('credentials') or {}
            for c in credentials.values():
                entry = {"id": c['ID'],
                         "account_group": c['ACCOUNT_GROUP'],
                         "added_timestamp": c['ADDED_TIMESTAMP'],
                         "assigned_dcns": list(c['ASSIGNED_DCNS'])}
                if reveal_secrets:
                    entry['api_key'] = c['API_KEY']
                    entry['api_secret'] = c['API_SECRET']
                else:
                    entry['api_key_preview'] = self._mask(c['API_KEY'])
                result.append(entry)
        return result

    def release_credentials(self, uid: str = None) -> bool:
        """Remove uid from ASSIGNED_DCNS of all credentials (called when DCN
        pod disappears)."""
        if uid is None:
            raise ValueError("Missing mandatory parameter: uid")
        with self.data_lock:
            credentials = self.data.get('credentials') or {}
            changed = False
            for c in credentials.values():
                if uid in c['ASSIGNED_DCNS']:
                    c['ASSIGNED_DCNS'].remove(uid)
                    changed = True
            if changed:
                self._set_update_timestamp()
        return changed

    @staticmethod
    def _mask(secret: str) -> str:
        if not secret:
            return ""
        if len(secret) <= 6:
            return "*" * len(secret)
        return secret[:4] + "*" * (len(secret) - 6) + secret[-2:]

    def delete(self, key: str = None) -> bool:
        with self.data_lock:
            if key in self.data:
                del self.data[key]
                self._set_update_timestamp()
                self.app.stdout_msg(f"DB entry deleted: {key}", log="debug", stdout=False)
                return True
        self.app.stdout_msg(f"DB entry {key} not found.", log="debug", stdout=False)
        return False

    def delete_depthcache(self, exchange: str = None, market: str = None) -> bool:
        if exchange is None or market is None:
            raise ValueError("Missing mandatory parameter: exchange, market")
        with self.data_lock:
            try:
                del self.data["depthcaches"][exchange][market]
            except KeyError:
                return True
            self._set_update_timestamp()
        self.app.stdout_msg(f"DB depthcaches deleted: {exchange}, {market}", log="debug")
        return True

    def delete_depthcache_distribution(self, exchange: str = None, market: str = None, pod_uid: str = None) -> bool:
        if exchange is None or market is None or pod_uid is None:
            raise ValueError("Missing mandatory parameter: exchange, pod_uid, market")
        with self.data_lock:
            del self.data["depthcaches"][exchange][market]['DISTRIBUTION'][pod_uid]
            self.data['depthcaches'][exchange][market]['DISTRIBUTION_CHANGES'] = \
                self.data['depthcaches'][exchange][market].get('DISTRIBUTION_CHANGES', 0) + 1
            self.data['depthcaches'][exchange][market]['LAST_DISTRIBUTION_CHANGE'] = \
                self.app.get_unix_timestamp()
            self._set_update_timestamp()
        self.app.stdout_msg(f"DB depthcache distribution deleted: {exchange}, {market}, {pod_uid}", log="debug")
        return True

    def delete_pod(self, uid: str = None) -> bool:
        if uid is None:
            raise ValueError("Missing mandatory parameter: uid")
        with self.data_lock:
            del self.data["pods"][uid]
            self._set_update_timestamp()
        self.app.stdout_msg(f"DB pod deleted: {uid}", log="debug", stdout=True)
        return True

    def delete_old_pods(self) -> bool:
        old_pods = []
        max_age = 60
        with self.data_lock:
            for uid in self.data['pods']:
                if (time.time() - max_age) > self.data['pods'][uid]['LAST_SEEN']:
                    old_pods.append(uid)
        for uid in old_pods:
            self.delete_pod(uid=uid)
        return True

    def exists_depthcache(self, exchange: str = None, market: str = None) -> bool:
        if exchange is None or market is None:
            raise ValueError("Missing mandatory parameter: exchange, market")
        with self.data_lock:
            try:
                return market in self.data['depthcaches'][exchange]
            except KeyError:
                return False

    def exists_pod(self, uid: str = None) -> bool:
        if uid is None:
            raise ValueError("Missing mandatory parameter: uid")
        return uid in self.data['pods']

    def get(self, key: str = None):
        with self.data_lock:
            return self.data.get(key)

    def get_all(self) -> dict:
        with self.data_lock:
            return self.data

    def get_available_dcn_pods(self) -> dict:
        available_dcn_pods = {}
        for uid in self.data['pods']:
            if self.data['pods'][uid]['ROLE'] == "ubdcc-dcn":
                try:
                    available_dcn_pods[uid] = self.data['nodes'][self.data['pods'][uid]['NODE']]['USAGE_CPU_PERCENT']
                except KeyError:
                    available_dcn_pods[uid] = 0
        return available_dcn_pods

    def get_backup_dict(self) -> dict:
        with self.data_lock:
            return self.app.sort_dict(input_dict=self.app.data['db'].data)

    def get_best_dcn(self, available_pods: dict = None, excluded_pods: list = None) -> str | None:
        if available_pods is None:
            available_pods = self.get_available_dcn_pods()
        for uid in excluded_pods:
            try:
                del available_pods[uid]
            except KeyError:
                pass
        available_pods_uid: list = [uid for uid in available_pods.keys()]
        return self.app.get_dcn_uid_unused_longest_time(selection=available_pods_uid)

    def get_dcn_responsibilities(self) -> list:
        with (self.data_lock):
            responsibilities = []
            for exchange in self.data['depthcaches']:
                for market in self.data['depthcaches'][exchange]:
                    for pod_uid in self.data['depthcaches'][exchange][market]['DISTRIBUTION']:
                        if pod_uid == self.app.id['uid'] and \
                            self.data['depthcaches'][exchange][market]['DISTRIBUTION'][pod_uid]['SCHEDULED_START_TIME'] < \
                                self.app.get_unix_timestamp():
                            responsibilities.append({"exchange": exchange,
                                                     "market": market,
                                                     "refresh_interval": self.data['depthcaches'][exchange][market]['REFRESH_INTERVAL'],
                                                     "update_interval": self.data['depthcaches'][exchange][market]['UPDATE_INTERVAL']})
        return responsibilities

    def get_depthcache_list(self) -> dict:
        with self.data_lock:
            try:
                return self.data['depthcaches']
            except KeyError:
                return {}

    def get_depthcache_info(self, exchange: str = None, market: str = None) -> dict:
        if exchange is None or market is None:
            raise ValueError("Missing mandatory parameter: exchange, market")
        with self.data_lock:
            try:
                return self.data['depthcaches'][exchange][market]
            except KeyError:
                return {}

    def get_pod_by_address(self, address: str = None) -> dict | None:
        if address is None:
            raise ValueError("Missing mandatory parameter: address")
        with self.data_lock:
            try:
                for uid in self.data['pods']:
                    if self.data['pods'][uid]['IP'] == address:
                        return self.data['pods'][uid]
            except KeyError:
                return None

    def get_pod_by_uid(self, uid=None) -> dict | None:
        if uid is None:
            raise ValueError("Missing mandatory parameter: uid")
        with self.data_lock:
            try:
                return self.data['pods'][uid]
            except KeyError:
                return None

    def get_responsible_dcn_addresses(self, exchange: str = None, market: str = None) -> list:
        with self.data_lock:
            responsible_dcn = []
            try:
                for pod_uid in self.data['depthcaches'][exchange][market]['DISTRIBUTION']:
                    if self.data['depthcaches'][exchange][market]['DISTRIBUTION'][pod_uid]['STATUS'] == "running":
                        responsible_dcn.append([self.data['pods'][pod_uid]['IP'],
                                                self.data['pods'][pod_uid]['API_PORT_REST'],
                                                pod_uid])
            except KeyError:
                pass
        return responsible_dcn

    def get_worst_dcn(self, available_pods: dict | None = None, excluded_pods: list = None) -> str | None:
        if available_pods is None:
            available_pods = self.get_available_dcn_pods()
        # Todo:  Find worst pod (cpu or subscriptions or ...)
        worst_pod = None
        for uid in available_pods:
            if uid not in excluded_pods:
                worst_pod = uid
        return worst_pod

    def replace_data(self, data: dict = None):
        with self.data_lock:
            self.data = data
        return True

    def remove_orphaned_distribution_entries(self) -> bool:
        with self.data_lock:
            remove_distributions = []
            for exchange in self.data['depthcaches']:
                for market in self.data['depthcaches'][exchange]:
                    for pod_uid in self.data['depthcaches'][exchange][market]['DISTRIBUTION']:
                        if self.exists_pod(uid=pod_uid) is False:
                            remove_distributions.append({"exchange": exchange,
                                                         "market": market,
                                                         "pod_uid": pod_uid})
        with self.data_lock:
            for item in remove_distributions:
                del self.data['depthcaches'][item['exchange']][item['market']]['DISTRIBUTION'][item['pod_uid']]
                self._set_update_timestamp()
        return True

    def remove_orphaned_credential_assignments(self) -> bool:
        with self.data_lock:
            existing_pods = set(self.data.get('pods', {}).keys())
            credentials = self.data.get('credentials') or {}
            changed = False
            for c in credentials.values():
                new_list = [uid for uid in c['ASSIGNED_DCNS'] if uid in existing_pods]
                if len(new_list) != len(c['ASSIGNED_DCNS']):
                    c['ASSIGNED_DCNS'] = new_list
                    changed = True
            if changed:
                self._set_update_timestamp()
        return True

    def revise(self) -> bool:
        start_time = time.time()
        self.app.stdout_msg(f"Revise the Database ...", log="info")
        self.update_nodes()
        self.delete_old_pods()
        self.remove_orphaned_distribution_entries()
        self.remove_orphaned_credential_assignments()
        self.manage_distribution()
        run_time = time.time() - start_time
        self.app.stdout_msg(f"Database revised in {run_time} seconds!", log="info")
        return True

    def manage_distribution(self) -> bool:
        add_distributions = []
        remove_distributions = []
        with self.data_lock:
            for exchange in self.data['depthcaches']:
                print(f"exchange={exchange}")
                for market in self.data['depthcaches'][exchange]:
                    print(f"market={market}")
                    existing_distribution = []
                    for pod_uid in self.data['depthcaches'][exchange][market]['DISTRIBUTION']:
                        existing_distribution.append(pod_uid)
                    existing_quantity = len(self.data['depthcaches'][exchange][market]['DISTRIBUTION'])
                    desired_quantity = self.data['depthcaches'][exchange][market]['DESIRED_QUANTITY']
                    if existing_quantity < desired_quantity:
                        add_quantity = desired_quantity - existing_quantity
                        delayed_start_time: float = 300.0
                        for i in range(0, add_quantity):
                            best_dcn = self.get_best_dcn(excluded_pods=existing_distribution)
                            print(f"best_dcn={best_dcn}")
                            if best_dcn is not None:
                                if existing_quantity > 0:
                                    multiplikator = i + existing_quantity
                                else:
                                    multiplikator = i
                                scheduled_start_time = self.app.get_unix_timestamp() + float(multiplikator) * delayed_start_time
                                add_distributions.append({"exchange": exchange,
                                                          "market": market,
                                                          "pod_uid": best_dcn,
                                                          "scheduled_start_time": scheduled_start_time})
                                existing_distribution.append(best_dcn)
                                print(f"ADDED: {add_distributions}")
                                break
                    elif existing_quantity > desired_quantity:
                        remove_quantity = existing_quantity - desired_quantity
                        exclude_dcn = []
                        available_pods = {}
                        for uid in existing_distribution:
                            available_pods[uid] = uid
                        for _ in range(0, remove_quantity):
                            worst_dcn = self.get_worst_dcn(available_pods=available_pods,
                                                           excluded_pods=exclude_dcn)
                            if worst_dcn is not None:
                                exclude_dcn.append(worst_dcn)
                                remove_distributions.append({"exchange": exchange,
                                                             "market": market,
                                                             "pod_uid": worst_dcn})
        for item in add_distributions:
            self.add_depthcache_distribution(exchange=item['exchange'],
                                             market=item['market'],
                                             pod_uid=item['pod_uid'],
                                             scheduled_start_time=item['scheduled_start_time'])
        for item in remove_distributions:
            self.delete_depthcache_distribution(exchange=item['exchange'],
                                                market=item['market'],
                                                pod_uid=item['pod_uid'])
        return True

    def set(self, key: str = None, value: dict | str | float | list | set | tuple = None) -> bool:
        with self.data_lock:
            self.data[key] = value
            self._set_update_timestamp()
        self.app.stdout_msg(f"DB entry added/updated: {key} = {value}", log="debug", stdout=False)
        return True

    def update_nodes(self) -> bool:
        nodes = self.app.get_k8s_nodes()
        if nodes:
            self.set(key="nodes", value=nodes)
            self.app.stdout_msg(f"DB all nodes updated!", log="debug", stdout=False)
            return True
        else:
            self.app.stdout_msg(f"Timed update of the DB key 'nodes': Query of the k8s nodes was empty, no "
                                f"update is performed!", log="error", stdout=True)
            return False

    def update_depthcache(self,
                          desired_quantity: int = None,
                          exchange: str = None,
                          refresh_interval: int = None,
                          market: str = None,
                          update_interval: int = None) -> bool:
        if exchange is None or market is None:
            raise ValueError("Missing mandatory parameter: exchange, market")
        with self.data_lock:
            if desired_quantity is not None:
                self.data['depthcaches'][exchange][market]['DESIRED_QUANTITY'] = desired_quantity
                self._set_update_timestamp()
            if update_interval is not None:
                self.data['depthcaches'][exchange][market]['UPDATE_INTERVAL'] = update_interval
                self._set_update_timestamp()
            if refresh_interval is not None:
                self.data['depthcaches'][exchange][market]['REFRESH_INTERVAL'] = refresh_interval
                self._set_update_timestamp()
        self.app.stdout_msg(f"DB depthcaches updated: {exchange}, {market}, {desired_quantity}, {update_interval}",
                            log="debug")
        return True

    def update_depthcache_distribution(self,
                                       exchange: str = None,
                                       market: str = None,
                                       pod_uid: str = None,
                                       last_restart_time: float = None,
                                       status: str = None) -> bool:
        if exchange is None or market is None or pod_uid is None:
            raise ValueError("Missing mandatory parameter: exchange, pod_uid, market")
        with self.data_lock:
            if last_restart_time is not None:
                try:
                    dist = self.data['depthcaches'][exchange][market]['DISTRIBUTION'][pod_uid]
                except KeyError:
                    return False
                if last_restart_time != dist.get('LAST_RESTART_TIME'):
                    dist['LAST_RESTART_TIME'] = last_restart_time
                    dist['RESTARTS'] = dist.get('RESTARTS', 0) + 1
                    self._set_update_timestamp()
            if status is not None:
                try:
                    self.data['depthcaches'][exchange][market]['DISTRIBUTION'][pod_uid]['STATUS'] = status
                except KeyError:
                    return False
                self._set_update_timestamp()
        self.app.stdout_msg(f"DB depthcache distribution updated: {exchange}, {market}, {pod_uid}, {last_restart_time},"
                            f" {status}", log="debug")
        return True

    def update_pod(self, uid: str = None, node: str = None, ip: str = None, api_port_rest: int = None,
                   status: str = None) -> bool:
        if uid is None:
            raise ValueError("Missing mandatory parameter: uid")
        with self.data_lock:
            self.data['pods'][uid]['LAST_SEEN'] = self.app.get_unix_timestamp()
            if api_port_rest is not None:
                self.data['pods'][uid]['API_PORT_REST'] = api_port_rest
                self._set_update_timestamp()
            if ip is not None:
                self.data['pods'][uid]['IP'] = ip
                self._set_update_timestamp()
            if node is not None:
                self.data['pods'][uid]['NODE'] = node
                self._set_update_timestamp()
            if status is not None:
                self.data['pods'][uid]['STATUS'] = status
                self._set_update_timestamp()
        self.app.stdout_msg(f"DB pod updated: {uid}", log="debug", stdout=False)
        return True
