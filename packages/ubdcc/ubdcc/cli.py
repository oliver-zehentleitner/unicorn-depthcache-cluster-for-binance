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
    dcn_counter = [0]  # mutable for closure access

    def spawn_mgmt():
        log = open(os.path.join(logdir, "ubdcc-mgmt.log"), "a")
        proc = subprocess.Popen(
            [sys.executable, "-c",
             f"import os; from ubdcc_mgmt.Mgmt import Mgmt; Mgmt(cwd='{cwd}', mgmt_port={mgmt_port})"],
            stdout=log, stderr=subprocess.STDOUT
        )
        # Remove old mgmt from processes list
        for i, (name, p, l) in enumerate(processes):
            if name == "mgmt":
                processes.pop(i)
                break
        processes.append(("mgmt", proc, log))
        return proc.pid

    def spawn_restapi():
        log = open(os.path.join(logdir, "ubdcc-restapi.log"), "a")
        proc = subprocess.Popen(
            [sys.executable, "-c",
             f"import os; from ubdcc_restapi.RestApi import RestApi; RestApi(cwd='{cwd}', mgmt_port={mgmt_port})"],
            stdout=log, stderr=subprocess.STDOUT
        )
        # Remove old restapi from processes list
        for i, (name, p, l) in enumerate(processes):
            if name == "restapi":
                processes.pop(i)
                break
        processes.append(("restapi", proc, log))
        return proc.pid

    def spawn_dcn():
        dcn_counter[0] += 1
        nr = dcn_counter[0]
        log = open(os.path.join(logdir, f"ubdcc-dcn-{nr}.log"), "a")
        proc = subprocess.Popen(
            [sys.executable, "-c",
             f"import os; from ubdcc_dcn.DepthCacheNode import DepthCacheNode; "
             f"DepthCacheNode(cwd='{cwd}', mgmt_port={mgmt_port})"],
            stdout=log, stderr=subprocess.STDOUT
        )
        processes.append((f"dcn-{nr}", proc, log))
        return nr, proc.pid

    # Start mgmt
    pid = spawn_mgmt()
    print(f"  mgmt started (PID {pid})")

    # Start restapi
    pid = spawn_restapi()
    print(f"  restapi started (PID {pid})")

    # Start DCNs
    for i in range(dcn_count):
        nr, pid = spawn_dcn()
        print(f"  dcn-{nr} started (PID {pid})")

    expected_pods = 1 + dcn_count  # restapi + DCNs (mgmt doesn't register itself)
    print(f"\nWaiting for {expected_pods} pods to register with mgmt...")

    cluster_info = wait_for_cluster(mgmt_port, expected_pods)
    if cluster_info:
        print(f"Cluster is ready!\n")
        print_status_table(cluster_info, mgmt_port=mgmt_port)
    else:
        print("Warning: Timeout waiting for all pods to register. Check the logs.")

    print(f"\nType 'help' for available commands, Ctrl+C or 'stop' to shut down.\n")

    # Interactive console
    def do_shutdown():
        print("\nShutting down cluster...")
        shutdown_all(mgmt_port)
        for name, proc, log in processes:
            proc.terminate()
            log.close()
        try:
            os.remove(STATE_FILE)
        except FileNotFoundError:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, lambda sig, frame: do_shutdown())
    signal.signal(signal.SIGTERM, lambda sig, frame: do_shutdown())

    while True:
        try:
            raw = input("ubdcc> ").strip()
        except (KeyboardInterrupt, EOFError):
            do_shutdown()

        if not raw:
            continue
        parts = raw.split(None, 1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else None

        if cmd in ('status', '/status'):
            try:
                response = requests.get(f"http://127.0.0.1:{mgmt_port}/get_cluster_info", timeout=5)
                data = response.json()
                if data.get('result') == 'OK':
                    print()
                    print_status_table(data, mgmt_port=mgmt_port)
                    print()
            except requests.exceptions.ConnectionError:
                print("Cannot connect to mgmt.")
        elif cmd in ('stop', '/stop', 'quit', 'exit'):
            do_shutdown()
        elif cmd in ('add-dcn', '/add-dcn'):
            count = int(arg) if arg else 1
            for _ in range(count):
                nr, pid = spawn_dcn()
                print(f"  dcn-{nr} started (PID {pid})")
            print(f"Waiting for registration...")
            time.sleep(3)
        elif cmd in ('remove-dcn', '/remove-dcn'):
            if arg:
                remove_dcn(mgmt_port, arg, processes)
            else:
                print("Usage: remove-dcn <pod-name>")
        elif cmd in ('restart', '/restart'):
            if not arg:
                print("Usage: restart <pod-name|mgmt|restapi>")
            elif arg in ('ubdcc-mgmt', 'mgmt'):
                try:
                    requests.get(f"http://127.0.0.1:{mgmt_port}/shutdown", timeout=5)
                except requests.exceptions.ConnectionError:
                    pass
                time.sleep(2)
                pid = spawn_mgmt()
                print(f"  mgmt restarted (PID {pid})")
                time.sleep(3)
            elif arg in ('ubdcc-restapi', 'restapi'):
                # Find restapi port and shut it down
                try:
                    data = requests.get(f"http://127.0.0.1:{mgmt_port}/get_cluster_info", timeout=5).json()
                    for uid, pod in data.get('db', {}).get('pods', {}).items():
                        if pod.get('ROLE') == 'ubdcc-restapi':
                            requests.get(f"http://127.0.0.1:{pod['API_PORT_REST']}/shutdown", timeout=3)
                            break
                except requests.exceptions.ConnectionError:
                    pass
                time.sleep(2)
                pid = spawn_restapi()
                print(f"  restapi restarted (PID {pid})")
                time.sleep(3)
            else:
                # DCN or other pod by name
                restart_pod(mgmt_port, arg)
                time.sleep(2)
                nr, pid = spawn_dcn()
                print(f"  dcn-{nr} respawned (PID {pid})")
                time.sleep(3)
        elif cmd in ('help', '/help', '?'):
            print()
            print("Available commands:")
            print("  status            Show cluster status")
            print("  add-dcn [count]   Spawn new DCN process(es)")
            print("  remove-dcn <name> Stop and remove a DCN")
            print("  restart <name>    Restart a specific pod")
            print("  stop              Shut down the cluster")
            print("  help              Show this help")
            print()
        else:
            print(f"Unknown command: {cmd}. Type 'help' for available commands.")


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
    restart_pod(mgmt_port, args.name)


def remove_dcn(mgmt_port, target, processes):
    """Stop a DCN pod and remove it from the process list."""
    url = f"http://127.0.0.1:{mgmt_port}/get_cluster_info"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
    except requests.exceptions.ConnectionError:
        print(f"Cannot connect to mgmt on port {mgmt_port}.")
        return

    pods = data.get('db', {}).get('pods', {})
    for uid, pod in pods.items():
        if pod['NAME'] == target or uid == target:
            if pod.get('ROLE') != 'ubdcc-dcn':
                print(f"'{target}' is not a DCN. Use 'remove-dcn' only for DCN pods.")
                return
            port = pod['API_PORT_REST']
            name = pod['NAME']
            try:
                requests.get(f"http://127.0.0.1:{port}/shutdown", timeout=5)
                print(f"  Removed: {name} (port {port})")
            except requests.exceptions.ConnectionError:
                print(f"  Warning: Could not reach {name} on port {port}")
            # Remove from local process list
            for i, (pname, proc, log) in enumerate(processes):
                if proc.poll() is not None or pname.startswith('dcn'):
                    # Can't match by name since local names differ from pod names
                    # Just clean up dead processes
                    pass
            return

    print(f"Pod '{target}' not found. Use 'status' to see available pods.")


def restart_pod(mgmt_port, target):
    """Send shutdown to a specific pod by name or UID."""
    # Handle mgmt separately — it doesn't register itself in the pod list
    if target in ('ubdcc-mgmt', 'mgmt'):
        try:
            requests.get(f"http://127.0.0.1:{mgmt_port}/shutdown", timeout=5)
            print(f"Shutdown signal sent to mgmt on port {mgmt_port}.")
            print(f"Note: Restart the process manually or re-run 'ubdcc start'.")
        except requests.exceptions.ConnectionError:
            print(f"Cannot connect to mgmt on port {mgmt_port}.")
        return

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

    print(f"Pod '{target}' not found. Use 'status' to see available pods.")


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
