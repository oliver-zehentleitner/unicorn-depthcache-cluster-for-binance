#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ¯\_(ツ)_/¯
#
# File: packages/ubdcc-mgmt/ubdcc_mgmt/RestEndpoints.py
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

import orjson as json
from ubdcc_shared_modules.AccountGroups import ACCOUNT_GROUPS, is_valid_account_group
from ubdcc_shared_modules.Database import Database
from ubdcc_shared_modules.RestEndpointsBase import RestEndpointsBase, Request


class RestEndpoints(RestEndpointsBase):
    def __init__(self, app=None):
        super().__init__(app=app)
        self.db: Database = self.app.data['db']

    def register(self):
        super().register()

        @self.fastapi.get("/create_depthcache")
        async def create_depthcache(request: Request):
            return await self.create_depthcache(request=request)

        @self.fastapi.post("/create_depthcaches")
        async def create_depthcaches_post(request: Request):
            return await self.create_depthcaches(request=request)

        @self.fastapi.get("/create_depthcaches")
        async def create_depthcaches_get(request: Request):
            return await self.create_depthcaches(request=request)

        @self.fastapi.get("/get_cluster_info")
        async def get_cluster_info(request: Request):
            return await self.get_cluster_info(request=request)

        @self.fastapi.get("/get_depthcache_list")
        async def get_depthcache_list(request: Request):
            return await self.get_depthcache_list(request=request)

        @self.fastapi.get("/get_depthcache_info")
        async def get_depthcache_info(request: Request):
            return await self.get_depthcache_info(request=request)

        @self.fastapi.get("/stop_depthcache")
        async def stop_depthcache(request: Request):
            return await self.stop_depthcache(request=request)

        @self.fastapi.get("/ubdcc_get_responsible_dcn_addresses")
        async def ubdcc_get_responsible_dcn_addresses(request: Request):
            return await self.ubdcc_get_responsible_dcn_addresses(request=request)

        @self.fastapi.get("/ubdcc_node_cancellation")
        async def ubdcc_node_cancellation(request: Request):
            return await self.ubdcc_node_cancellation(request=request)

        @self.fastapi.get("/ubdcc_node_registration")
        async def ubdcc_node_registration(request: Request):
            return await self.ubdcc_node_registration(request=request)

        @self.fastapi.get("/ubdcc_node_sync")
        async def ubdcc_node_sync(request: Request):
            return await self.ubdcc_node_sync(request=request)

        @self.fastapi.get("/ubdcc_update_depthcache_distribution")
        async def ubdcc_update_depthcache_distribution(request: Request):
            return await self.ubdcc_update_depthcache_distribution(request=request)

        @self.fastapi.post("/ubdcc_add_credentials")
        async def ubdcc_add_credentials_post(request: Request):
            return await self.ubdcc_add_credentials(request=request)

        @self.fastapi.get("/ubdcc_add_credentials")
        async def ubdcc_add_credentials_get(request: Request):
            return await self.ubdcc_add_credentials(request=request)

        @self.fastapi.post("/ubdcc_remove_credentials")
        async def ubdcc_remove_credentials_post(request: Request):
            return await self.ubdcc_remove_credentials(request=request)

        @self.fastapi.get("/ubdcc_remove_credentials")
        async def ubdcc_remove_credentials_get(request: Request):
            return await self.ubdcc_remove_credentials(request=request)

        @self.fastapi.get("/ubdcc_get_credentials_list")
        async def ubdcc_get_credentials_list(request: Request):
            return await self.ubdcc_get_credentials_list(request=request)

        @self.fastapi.get("/ubdcc_assign_credentials")
        async def ubdcc_assign_credentials(request: Request):
            return await self.ubdcc_assign_credentials(request=request)

    async def create_depthcache(self, request: Request):
        event = "CREATE_DEPTHCACHE"
        ready_check = self.throw_error_if_mgmt_not_ready(request=request, event=event)
        if ready_check is not None:
            return ready_check
        exchange = request.query_params.get("exchange", None)
        market = request.query_params.get("market", None)
        desired_quantity = request.query_params.get("desired_quantity", None)
        update_interval = request.query_params.get("update_interval", None)
        refresh_interval = request.query_params.get("refresh_interval", None)
        if exchange == "None":
            exchange = None
        if market == "None":
            market = None
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
        if exchange is None or market is None:
            return self.get_error_response(event=event, error_id="#1016",
                                           message="Missing required parameter: exchange, market")
        if self.db.exists_depthcache(exchange=exchange, market=market):
            return self.get_error_response(event=event, error_id="#1024",
                                           message=f"DepthCache '{market}' for '{exchange}' already exists!")
        try:
            result = self.db.add_depthcache(exchange=exchange, market=market, update_interval=update_interval,
                                            refresh_interval=refresh_interval, desired_quantity=desired_quantity)
        except ValueError as error_msg:
            return self.get_error_response(event=event, error_id="#1017", message=str(error_msg))
        if result is True:
            # Todo:
            # Add Option to run:
            #  self.db.manage_distribution()
            return self.get_ok_response(event=event)
        else:
            return self.get_error_response(event=event, error_id="#1018", message="An unknown error has occurred!")

    async def create_depthcaches(self, request: Request):
        event = "CREATE_DEPTHCACHES"
        ready_check = self.throw_error_if_mgmt_not_ready(request=request, event=event)
        if ready_check is not None:
            return ready_check
        if request.method == "POST":
            body = json.loads(await request.body())
            exchange = body.get("exchange", None)
            markets = body.get("markets", None)
            desired_quantity = body.get("desired_quantity", None)
            update_interval = body.get("update_interval", None)
            refresh_interval = body.get("refresh_interval", None)
        else:
            exchange = request.query_params.get("exchange", None)
            markets_param = request.query_params.get("markets", None)
            markets = markets_param.split(",") if markets_param else None
            desired_quantity = request.query_params.get("desired_quantity", None)
            update_interval = request.query_params.get("update_interval", None)
            refresh_interval = request.query_params.get("refresh_interval", None)
        if exchange == "None":
            exchange = None
        if markets == "None":
            markets = None
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
        if exchange is None or markets is None:
            return self.get_error_response(event=event, error_id="#1016",
                                           message="Missing required parameter: exchange, markets")
        for market in markets:
            if self.db.exists_depthcache(exchange=exchange, market=market) is False:
                try:
                    result = self.db.add_depthcache(exchange=exchange,
                                                    market=market,
                                                    update_interval=update_interval,
                                                    refresh_interval=refresh_interval,
                                                    desired_quantity=desired_quantity)
                except ValueError as error_msg:
                    self.app.stdout(f"ERROR: {error_msg}", log="error")
                    continue
                if result is True:
                    pass
                    # Todo:
                    # Add Option to run:
                    #  self.db.manage_distribution()
                else:
                    return self.get_error_response(event=event, error_id="#1018",
                                                   message="An unknown error has occurred!")
        return self.get_ok_response(event=event)

    async def get_cluster_info(self, request: Request):
        event = "GET_CLUSTER_INFO"
        ready_check = self.throw_error_if_mgmt_not_ready(request=request, event=event)
        if ready_check is not None:
            return ready_check
        response = self.create_cluster_info_response()
        return self.get_ok_response(event=event, params=response)

    async def get_depthcache_list(self, request: Request):
        event = "GET_DEPTHCACHE_LIST"
        ready_check = self.throw_error_if_mgmt_not_ready(request=request, event=event)
        if ready_check is not None:
            return ready_check
        response = self.create_depthcache_list_response()
        return self.get_ok_response(event=event, params=response)

    async def get_depthcache_info(self, request: Request):
        event = "GET_DEPTHCACHE_INFO"
        ready_check = self.throw_error_if_mgmt_not_ready(request=request, event=event)
        if ready_check is not None:
            return ready_check
        exchange = request.query_params.get("exchange", None)
        market = request.query_params.get("market", None)
        if market == "None":
            exchange = None
        if market == "None":
            exchange = None
        if exchange is None or market is None:
            return self.get_error_response(event=event, error_id="#1006",
                                           message="Missing required parameter: exchange, market")
        response = self.create_depthcache_info_response(exchange=exchange, market=market)
        if not response['depthcache_info']:
            return self.get_error_response(event=event, error_id="#7000", message=f"DepthCache '{market}' for "
                                                                                  f"'{exchange}' not found!")
        return self.get_ok_response(event=event, params=response)

    async def stop_depthcache(self, request: Request):
        event = "STOP_DEPTHCACHE"
        ready_check = self.throw_error_if_mgmt_not_ready(request=request, event=event)
        if ready_check is not None:
            return ready_check
        exchange = request.query_params.get("exchange", None)
        market = request.query_params.get("market", None)
        if market == "None":
            exchange = None
        if market == "None":
            exchange = None
        if exchange is None or market is None:
            return self.get_error_response(event=event, error_id="#1019",
                                           message="Missing required parameter: exchange, market")
        if not self.db.exists_depthcache(exchange=exchange, market=market):
            return self.get_error_response(event=event, error_id="#7000", message=f"DepthCache '{market}' for "
                                                                                  f"'{exchange}' not found!")
        try:
            result = self.db.delete_depthcache(exchange=exchange, market=market)
        except ValueError as error_msg:
            return self.get_error_response(event=event, error_id="#1020", message=str(error_msg))
        if result is True:
            return self.get_ok_response(event=event)
        else:
            return self.get_error_response(event=event, error_id="#1021", message="An unknown error has occurred!")

    async def ubdcc_get_responsible_dcn_addresses(self, request: Request):
        event = "UBDCC_GET_RESPONSIBLE_DCN_ADDRESSES"
        ready_check = self.throw_error_if_mgmt_not_ready(request=request, event=event)
        if ready_check is not None:
            return ready_check
        exchange = request.query_params.get("exchange", None)
        market = request.query_params.get("market", None)
        if market == "None":
            exchange = None
        if market == "None":
            exchange = None
        if exchange is None or market is None:
            return self.get_error_response(event=event, error_id="#1012",
                                           message="Missing required parameter: exchange, market")
        result = self.db.get_responsible_dcn_addresses(exchange=exchange, market=market)
        if result is True:
            return self.get_ok_response(event=event, params={"addresses": result})
        else:
            return self.get_error_response(event=event, error_id="#1013",
                                           message=f"No addresses of responsible DCN for '{market}' from '{exchange}' "
                                                   f"found!")

    async def ubdcc_node_cancellation(self, request: Request):
        event = "UBDCC_NODE_CANCELLATION"
        ready_check = self.throw_error_if_mgmt_not_ready(request=request, event=event)
        if ready_check is not None:
            return ready_check
        uid = request.query_params.get("uid")
        if uid == "None":
            uid = None
        if uid is None:
            return self.get_error_response(event=event, error_id="#1004", message="Missing required parameter: uid")
        if not self.db.exists_pod(uid=uid):
            return self.get_error_response(event=event, error_id="#1005",
                                           message=f"A pod with the uid '{uid}' does not exist!")
        result = self.db.delete_pod(uid=uid)
        if result is True:
            return self.get_ok_response(event=event)
        else:
            return self.get_error_response(event=event, error_id="#1008", message="An unknown error has occurred!")

    async def ubdcc_node_registration(self, request: Request):
        event = "UBDCC_NODE_REGISTRATION"
        ready_check = self.throw_error_if_mgmt_not_ready(request=request, event=event)
        if ready_check is not None:
            return ready_check
        name = request.query_params.get("name", None)
        uid = request.query_params.get("uid", None)
        node = request.query_params.get("node", None)
        role = request.query_params.get("role", None)
        api_port_rest = request.query_params.get("api_port_rest", None)
        status = request.query_params.get("status", None)
        ubldc_version = request.query_params.get("ubldc_version", None)
        version = request.query_params.get("version", None)
        if name == "None":
            name = None
        if uid == "None":
            uid = None
        if node == "None":
            node = None
        if role == "None":
            role = None
        if api_port_rest == "None":
            api_port_rest = None
        if status == "None":
            status = None
        if ubldc_version == "None":
            ubldc_version = None
        if version == "None":
            version = None
        if name is None or uid is None or node is None or role is None or api_port_rest is None or status is None:
            return self.get_error_response(event=event, error_id="#1002",
                                           message="Missing required parameter: name, uid, node, role, api_port_rest, "
                                                   "status")
        if self.db.exists_pod(uid=uid):
            return self.get_error_response(event=event, error_id="#1003",
                                           message=f"A pod with the uid '{uid}' already exists!")
        result = self.db.add_pod(name=name,
                                 uid=uid,
                                 node=node,
                                 role=role,
                                 ip=request.client.host,
                                 api_port_rest=int(api_port_rest),
                                 ubldc_version=ubldc_version,
                                 status=status,
                                 version=version)
        if result is True:
            await self.app.send_backup_to_node(host=request.client.host, port=api_port_rest)
            return self.get_ok_response(event=event)
        else:
            return self.get_error_response(event=event, error_id="#1009", message="An unknown error has occurred!")

    async def ubdcc_node_sync(self, request: Request):
        event = "UBDCC_NODE_SYNC"
        uid = request.query_params.get("uid", None)
        node = request.query_params.get("node", None)
        api_port_rest = request.query_params.get("api_port_rest", None)
        status = request.query_params.get("status", None)
        if uid == "None":
            uid = None
        if node == "None":
            node = None
        if api_port_rest == "None":
            api_port_rest = None
        if status == "None":
            status = None
        if uid is None or api_port_rest is None:
            return self.get_error_response(event=event, error_id="#1000",
                                           message="Missing required parameter: uid, api_port_rest")
        if not self.db.exists_pod(uid=uid) and self.db.is_empty() is True:
            backup = await self.app.get_backup_from_node(host=request.client.host, port=api_port_rest)
            if backup is not None:
                source_ip = request.client.host
                source_port = api_port_rest
                source_uid = uid
                timestamp_limit = float(backup['timestamp'])
                pods = []
                for pod in backup['pods']:
                    pods.append(backup['pods'][pod]['UID'])
                    timestamp = await self.app.get_backup_timestamp_from_node(host=backup['pods'][pod]['IP'],
                                                                              port=backup['pods'][pod]['API_PORT_REST'])
                    if timestamp is not None:
                        if timestamp_limit < timestamp:
                            source_ip = pod['IP']
                            source_port = pod['API_PORT_REST']
                            source_uid = pod['UID']
                            timestamp_limit = timestamp
                self.app.stdout_msg(f"Found pods: {pods}", log="info")
                if source_uid != uid:
                    backup = await self.app.get_backup_from_node(host=source_ip, port=source_port)
                if backup is not None:
                    self.db.replace_data(data=backup)

                    self.app.data['is_ready'] = True
                    self.app.stdout_msg(f"Loaded database from pod '{source_uid}'!", log="info")
        if not self.db.exists_pod(uid=uid):
            return self.get_error_response(event=event, error_id="#1001",
                                           message=f"Registration for pod '{uid}' not found!")

        result = self.db.update_pod(uid=uid,
                                    node=node,
                                    ip=request.client.host,
                                    status=status)
        pod = self.db.get_pod_by_uid(uid=uid)
        if result is True:
            await self.app.send_backup_to_node(host=request.client.host, port=pod['API_PORT_REST'])
            return self.get_ok_response(event=event)
        else:
            return self.get_error_response(event=event, error_id="#1010",
                                           message="An unknown error has occurred!")

    async def ubdcc_add_credentials(self, request: Request):
        event = "UBDCC_ADD_CREDENTIALS"
        ready_check = self.throw_error_if_mgmt_not_ready(request=request, event=event)
        if ready_check is not None:
            return ready_check
        if request.method == "POST":
            try:
                body = json.loads(await request.body())
            except Exception:
                body = {}
            account_group = body.get("account_group")
            api_key = body.get("api_key")
            api_secret = body.get("api_secret")
        else:
            account_group = request.query_params.get("account_group")
            api_key = request.query_params.get("api_key")
            api_secret = request.query_params.get("api_secret")
        if account_group == "None":
            account_group = None
        if account_group is None or api_key is None or api_secret is None:
            return self.get_error_response(event=event, error_id="#1030",
                                           message="Missing required parameter: account_group, api_key, api_secret")
        if not is_valid_account_group(account_group):
            return self.get_error_response(event=event, error_id="#1031",
                                           message=f"Invalid account_group '{account_group}'. "
                                                   f"Valid groups: {', '.join(ACCOUNT_GROUPS)}")
        try:
            credential_id = self.db.add_credentials(account_group=account_group,
                                                    api_key=api_key, api_secret=api_secret)
        except ValueError as error_msg:
            return self.get_error_response(event=event, error_id="#1032", message=str(error_msg))
        return self.get_ok_response(event=event, params={"id": credential_id})

    async def ubdcc_remove_credentials(self, request: Request):
        event = "UBDCC_REMOVE_CREDENTIALS"
        ready_check = self.throw_error_if_mgmt_not_ready(request=request, event=event)
        if ready_check is not None:
            return ready_check
        if request.method == "POST":
            try:
                body = json.loads(await request.body())
            except Exception:
                body = {}
            credential_id = body.get("id")
        else:
            credential_id = request.query_params.get("id")
        if credential_id == "None":
            credential_id = None
        if credential_id is None:
            return self.get_error_response(event=event, error_id="#1033",
                                           message="Missing required parameter: id")
        if self.db.delete_credentials(credential_id=credential_id):
            return self.get_ok_response(event=event)
        return self.get_error_response(event=event, error_id="#1034",
                                       message=f"Credentials '{credential_id}' not found!")

    async def ubdcc_get_credentials_list(self, request: Request):
        event = "UBDCC_GET_CREDENTIALS_LIST"
        ready_check = self.throw_error_if_mgmt_not_ready(request=request, event=event)
        if ready_check is not None:
            return ready_check
        credentials = self.db.get_credentials_list(reveal_secrets=False)
        return self.get_ok_response(event=event, params={"credentials": credentials})

    async def ubdcc_assign_credentials(self, request: Request):
        event = "UBDCC_ASSIGN_CREDENTIALS"
        ready_check = self.throw_error_if_mgmt_not_ready(request=request, event=event)
        if ready_check is not None:
            return ready_check
        uid = request.query_params.get("uid")
        account_group = request.query_params.get("account_group")
        if uid == "None":
            uid = None
        if account_group == "None":
            account_group = None
        if uid is None or account_group is None:
            return self.get_error_response(event=event, error_id="#1035",
                                           message="Missing required parameter: uid, account_group")
        if not is_valid_account_group(account_group):
            return self.get_error_response(event=event, error_id="#1036",
                                           message=f"Invalid account_group '{account_group}'")
        credential = self.db.assign_credentials(uid=uid, account_group=account_group)
        if credential is None:
            return self.get_ok_response(event=event, params={"credential": None})
        return self.get_ok_response(event=event,
                                    params={"credential": {"id": credential['ID'],
                                                           "account_group": credential['ACCOUNT_GROUP'],
                                                           "api_key": credential['API_KEY'],
                                                           "api_secret": credential['API_SECRET']}})

    async def ubdcc_update_depthcache_distribution(self, request: Request):
        event = "UBDCC_UPDATE_DEPTHCACHE_DISTRIBUTION"
        ready_check = self.throw_error_if_mgmt_not_ready(request=request, event=event)
        if ready_check is not None:
            return ready_check
        exchange = request.query_params.get("exchange", None)
        market = request.query_params.get("market", None)
        pod_uid = request.query_params.get("pod_uid", None)
        last_restart_time = request.query_params.get("last_restart_time", None)
        status = request.query_params.get("status", None)
        if exchange == "None":
            exchange = None
        if market == "None":
            market = None
        if pod_uid == "None":
            pod_uid = None
        if last_restart_time == "None":
            last_restart_time = None
        elif last_restart_time is not None:
            try:
                last_restart_time = float(last_restart_time)
            except (TypeError, ValueError):
                return self.get_error_response(event=event, error_id="#1024",
                                               message=f"Invalid last_restart_time value: "
                                                       f"{last_restart_time!r}")
        if status == "None":
            status = None
        if exchange is None or market is None or pod_uid is None:
            return self.get_error_response(event=event, error_id="#1015",
                                           message="Missing required parameter: exchange, market, pod_uid")
        if last_restart_time is None and status is None:
            return self.get_error_response(event=event, error_id="#1022",
                                           message="Nothing to update! Missing parameter: last_restart_time, status")
        result = self.db.update_depthcache_distribution(exchange=exchange, market=market,
                                                        pod_uid=pod_uid,
                                                        last_restart_time=last_restart_time,
                                                        status=status)
        if result is True:
            return self.get_ok_response(event=event)
        else:
            return self.get_error_response(event=event, error_id="#1023", message=f"DepthCache '{exchange} {market} "
                                                                                  f"{pod_uid}' not found!")
