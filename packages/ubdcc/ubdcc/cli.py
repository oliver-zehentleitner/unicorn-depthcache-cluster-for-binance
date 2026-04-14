#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ¯\_(ツ)_/¯
#
# File: packages/ubdcc/ubdcc/cli.py
#
# Project website: https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster
# Github: https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster
# Documentation: https://oliver-zehentleitner.github.io/unicorn-binance-depth-cache-cluster
# PyPI: https://pypi.org/project/ubdcc
#
# License: MIT
# https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/blob/master/LICENSE
#
# Author: Oliver Zehentleitner
#
# Copyright (c) 2024-2026, Oliver Zehentleitner (https://about.me/oliver-zehentleitner)
# All rights reserved.

import argparse
import os
import signal
import socket
import subprocess
import sys
import time

import requests

from ubdcc import __version__

STATE_FILE = ".ubdcc"
DEFAULT_MGMT_PORT = 42080


def save_port(port):
    with open(STATE_FILE, "w") as f:
        f.write(str(port))


def load_port():
    try:
        with open(STATE_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def get_mgmt_port(args):
    """Resolve mgmt port: --port flag > state file > default."""
    if args.port is not None:
        return args.port
    saved = load_port()
    if saved is not None:
        return saved
    return DEFAULT_MGMT_PORT


def is_port_free(port, host='127.0.0.1'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def find_free_port(start=42080):
    port = start
    while not is_port_free(port):
        port += 1
    return port


def wait_for_cluster(mgmt_port, expected_pods, timeout=120):
    """Poll get_cluster_info until all expected pods are registered."""
    url = f"http://127.0.0.1:{mgmt_port}/get_cluster_info"
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            if data.get('result') == 'OK' and data.get('db', {}).get('pods'):
                registered = len(data['db']['pods'])
                if registered >= expected_pods:
                    return data
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            pass
        time.sleep(1)
    return None


def cmd_start(args):
    mgmt_port = args.port if args.port else find_free_port(DEFAULT_MGMT_PORT)
    dcn_count = args.dcn
    logdir = args.logdir if args.logdir else os.getcwd()
    os.makedirs(logdir, exist_ok=True)
    save_port(mgmt_port)

    print(f"UBDCC Cluster Manager v{__version__}")
    print(f"Starting cluster with mgmt port {mgmt_port}, {dcn_count} DCN(s)...")
    print(f"Log directory: {logdir}")

    processes = []
    cwd = os.getcwd()

    # Start mgmt
    mgmt_log = open(os.path.join(logdir, "ubdcc-mgmt.log"), "w")
    mgmt_proc = subprocess.Popen(
        [sys.executable, "-c",
         f"import os; from ubdcc_mgmt.Mgmt import Mgmt; Mgmt(cwd='{cwd}', mgmt_port={mgmt_port})"],
        stdout=mgmt_log, stderr=subprocess.STDOUT
    )
    processes.append(("mgmt", mgmt_proc, mgmt_log))
    print(f"  mgmt started (PID {mgmt_proc.pid})")

    # Start restapi
    restapi_log = open(os.path.join(logdir, "ubdcc-restapi.log"), "w")
    restapi_proc = subprocess.Popen(
        [sys.executable, "-c",
         f"import os; from ubdcc_restapi.RestApi import RestApi; RestApi(cwd='{cwd}', mgmt_port={mgmt_port})"],
        stdout=restapi_log, stderr=subprocess.STDOUT
    )
    processes.append(("restapi", restapi_proc, restapi_log))
    print(f"  restapi started (PID {restapi_proc.pid})")

    # Start DCNs
    for i in range(dcn_count):
        dcn_log = open(os.path.join(logdir, f"ubdcc-dcn-{i+1}.log"), "w")
        dcn_proc = subprocess.Popen(
            [sys.executable, "-c",
             f"import os; from ubdcc_dcn.DepthCacheNode import DepthCacheNode; "
             f"DepthCacheNode(cwd='{cwd}', mgmt_port={mgmt_port})"],
            stdout=dcn_log, stderr=subprocess.STDOUT
        )
        processes.append((f"dcn-{i+1}", dcn_proc, dcn_log))
        print(f"  dcn-{i+1} started (PID {dcn_proc.pid})")

    expected_pods = 1 + dcn_count  # restapi + DCNs (mgmt doesn't register itself)
    print(f"\nWaiting for {expected_pods} pods to register with mgmt...")

    cluster_info = wait_for_cluster(mgmt_port, expected_pods)
    if cluster_info:
        print(f"Cluster is ready!\n")
        print_status_table(cluster_info, mgmt_port=mgmt_port)
    else:
        print("Warning: Timeout waiting for all pods to register. Check the logs.")

    print(f"\nUse 'ubdcc status' to check.")
    print(f"Use 'ubdcc stop' to shut down.\n")

    # Keep running, wait for Ctrl+C
    def signal_handler(sig, frame):
        print("\nReceived interrupt, shutting down cluster...")
        shutdown_all(mgmt_port)
        for name, proc, log in processes:
            proc.terminate()
            log.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        while True:
            # Check if any process died
            for name, proc, log in processes:
                if proc.poll() is not None:
                    print(f"Warning: {name} (PID {proc.pid}) has exited with code {proc.returncode}")
            time.sleep(5)
    except KeyboardInterrupt:
        signal_handler(None, None)


def cmd_status(args):
    mgmt_port = get_mgmt_port(args)
    url = f"http://127.0.0.1:{mgmt_port}/get_cluster_info"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get('result') == 'OK':
            print_status_table(data, mgmt_port=mgmt_port)
        else:
            print(f"Error: {data.get('message', 'Unknown error')}")
    except requests.exceptions.ConnectionError:
        print(f"Cannot connect to mgmt on port {mgmt_port}. Is the cluster running?")


def cmd_stop(args):
    mgmt_port = get_mgmt_port(args)
    shutdown_all(mgmt_port)


def cmd_restart(args):
    mgmt_port = get_mgmt_port(args)
    target = args.name
    url = f"http://127.0.0.1:{mgmt_port}/get_cluster_info"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
    except requests.exceptions.ConnectionError:
        print(f"Cannot connect to mgmt on port {mgmt_port}. Is the cluster running?")
        return

    pods = data.get('db', {}).get('pods', {})
    for uid, pod in pods.items():
        if pod['NAME'] == target or uid == target:
            port = pod['API_PORT_REST']
            name = pod['NAME']
            try:
                requests.get(f"http://127.0.0.1:{port}/shutdown", timeout=5)
                print(f"Shutdown signal sent to '{name}' on port {port}.")
                print(f"Note: Restart the process manually or re-run 'ubdcc start'.")
            except requests.exceptions.ConnectionError:
                print(f"Cannot connect to '{name}' on port {port}.")
            return

    print(f"Pod '{target}' not found. Use 'ubdcc status' to see available pods.")


def shutdown_all(mgmt_port):
    """Shutdown all pods via their /shutdown endpoints."""
    url = f"http://127.0.0.1:{mgmt_port}/get_cluster_info"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
    except requests.exceptions.ConnectionError:
        print(f"Cannot connect to mgmt on port {mgmt_port}.")
        return

    pods = data.get('db', {}).get('pods', {})
    for uid, pod in pods.items():
        port = pod['API_PORT_REST']
        name = pod['NAME']
        try:
            requests.get(f"http://127.0.0.1:{port}/shutdown", timeout=3)
            print(f"  Shutdown: {name} ({pod['ROLE']}) on port {port}")
        except requests.exceptions.ConnectionError:
            print(f"  Warning: Could not reach {name} on port {port}")

    # Shutdown mgmt last
    try:
        requests.get(f"http://127.0.0.1:{mgmt_port}/shutdown", timeout=3)
        print(f"  Shutdown: mgmt on port {mgmt_port}")
    except requests.exceptions.ConnectionError:
        print(f"  Warning: Could not reach mgmt on port {mgmt_port}")

    print("Cluster shutdown complete.")


def print_status_table(data, mgmt_port=42080):
    """Print a formatted status table from cluster info."""
    pods = data.get('db', {}).get('pods', {})

    print(f"{'ROLE':<16} {'NAME':<20} {'PORT':<8} {'STATUS':<10} {'VERSION'}")
    print("-" * 70)

    # Get mgmt info via /test endpoint
    try:
        mgmt_response = requests.get(f"http://127.0.0.1:{mgmt_port}/test", timeout=3)
        mgmt_data = mgmt_response.json()
        mgmt_name = mgmt_data.get('app', {}).get('name', '?')
        mgmt_version = mgmt_data.get('app', {}).get('version', '?')
        print(f"{'ubdcc-mgmt':<16} {mgmt_name:<20} {mgmt_port:<8} {'running':<10} {mgmt_version}")
    except requests.exceptions.ConnectionError:
        print(f"{'ubdcc-mgmt':<16} {'?':<20} {mgmt_port:<8} {'down':<10} {'?'}")

    # Sort: restapi first, then dcn
    role_order = {'ubdcc-restapi': 0, 'ubdcc-dcn': 1}
    sorted_pods = sorted(pods.values(), key=lambda p: (role_order.get(p.get('ROLE', ''), 9), p.get('NAME', '')))

    restapi_port = None
    for pod in sorted_pods:
        role = pod.get('ROLE', '?')
        name = pod.get('NAME', '?')
        port = pod.get('API_PORT_REST', '?')
        status = pod.get('STATUS', '?')
        version = pod.get('VERSION', '?')
        print(f"{role:<16} {name:<20} {port:<8} {status:<10} {version}")
        if role == 'ubdcc-restapi' and restapi_port is None:
            restapi_port = port

    depthcaches = data.get('db', {}).get('depthcaches', {})
    dc_count = sum(len(markets) for markets in depthcaches.values())
    print(f"\nDepthCaches: {dc_count}")
    print(f"Version: {data.get('version', '?')}")
    if restapi_port:
        print(f"\nREST API: http://127.0.0.1:{restapi_port}/")
        print(f"Cluster info: http://127.0.0.1:{restapi_port}/get_cluster_info")


def main():
    parser = argparse.ArgumentParser(
        prog='ubdcc',
        description='UNICORN Binance DepthCache Cluster — Cluster Manager'
    )
    parser.add_argument('-v', '--version', action='version', version=f'ubdcc {__version__}')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # start
    start_parser = subparsers.add_parser('start', help='Start the cluster')
    start_parser.add_argument('--dcn', type=int, default=1, help='Number of DCN processes (default: 1)')
    start_parser.add_argument('--port', type=int, default=None, help='Mgmt port (default: 42080 or next free)')
    start_parser.add_argument('--logdir', type=str, default=None, help='Log directory (default: current directory)')

    # status
    status_parser = subparsers.add_parser('status', help='Show cluster status')
    status_parser.add_argument('--port', type=int, default=None, help='Mgmt port (default: 42080)')

    # stop
    stop_parser = subparsers.add_parser('stop', help='Stop the cluster')
    stop_parser.add_argument('--port', type=int, default=None, help='Mgmt port (default: 42080)')

    # restart
    restart_parser = subparsers.add_parser('restart', help='Restart a specific pod')
    restart_parser.add_argument('name', help='Pod name or UID to restart')
    restart_parser.add_argument('--port', type=int, default=None, help='Mgmt port (default: 42080)')

    args = parser.parse_args()

    if args.command == 'start':
        cmd_start(args)
    elif args.command == 'status':
        cmd_status(args)
    elif args.command == 'stop':
        cmd_stop(args)
    elif args.command == 'restart':
        cmd_restart(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
