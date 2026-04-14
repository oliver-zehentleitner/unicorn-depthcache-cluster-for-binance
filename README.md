[![GitHub Release](https://img.shields.io/github/release/oliver-zehentleitner/unicorn-binance-depth-cache-cluster.svg?label=github)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/releases)
[![GitHub Downloads](https://img.shields.io/github/downloads/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/total?color=blue)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/releases)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://oliver-zehentleitner.github.io/unicorn-binance-depth-cache-cluster/license.html)
[![codecov](https://codecov.io/gh/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/branch/master/graph/badge.svg?token=5I03AZ3F5S)](https://codecov.io/gh/oliver-zehentleitner/unicorn-binance-depth-cache-cluster)
[![CodeQL](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/actions/workflows/codeql.yml/badge.svg)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/actions/workflows/codeql.yml)
[![Unit Tests](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/actions/workflows/unit-tests.yml)
[![Build and Publish PyPi (ubdcc-dcn)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/actions/workflows/build_wheels_ubdcc_dcn.yml/badge.svg)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/actions/workflows/build_wheels_ubdcc_dcn.yml)
[![Build and Publish PyPi (ubdcc-mgmt)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/actions/workflows/build_wheels_ubdcc_mgmt.yml/badge.svg)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/actions/workflows/build_wheels_ubdcc_mgmt.yml)
[![Build and Publish PyPi (ubdcc-restapi)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/actions/workflows/build_wheels_ubdcc_restapi.yml/badge.svg)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/actions/workflows/build_wheels_ubdcc_restapi.yml)
[![Build and Publish PyPi (ubdcc-shared-modules)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/actions/workflows/build_wheels_ubdcc_shared_modules.yml/badge.svg)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/actions/workflows/build_wheels_ubdcc_shared_modules.yml)
[![Read the Docs](https://img.shields.io/badge/read-%20docs-yellow)](https://oliver-zehentleitner.github.io/unicorn-binance-depth-cache-cluster)
[![Github](https://img.shields.io/badge/source-github-cbc2c8)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster)
[![Telegram](https://img.shields.io/badge/community-telegram-41ab8c)](https://t.me/unicorndevs)

# UNICORN Binance DepthCache Cluster (UBDCC)

Manage hundreds of Binance order book depth caches and access them via REST API — from any programming language, 
any number of clients, with load balancing and automatic failover. Simple to set up: `pip install`, start three 
processes, done.

Built on [UNICORN Binance Local Depth Cache (UBLDC)](https://github.com/oliver-zehentleitner/unicorn-binance-local-depth-cache). 
Part of the [UNICORN Binance Suite](https://github.com/oliver-zehentleitner/unicorn-binance-suite).

## What is UBDCC?

UBDCC turns Binance DepthCaches into a service. Instead of managing WebSocket connections and order book 
synchronization inside your trading bot, you run UBDCC as a standalone system and query it over HTTP whenever you need 
order book data.

It works in two ways:

- **On a single machine** — run a few processes locally and share DepthCache data between multiple bots, scripts or 
backtests on the same PC. No Kubernetes needed.
- **On a Kubernetes cluster** — scale across multiple servers with redundancy, multiple public IPs for higher Binance 
API throughput, and automatic state recovery if pods restart.

## Architecture

The system consists of three components:
- **mgmt** (1x) — manages the cluster state and distributes DepthCaches across nodes
- **restapi** (1-3x) — REST API gateway, load-balances data requests to DCN processes
- **dcn** (multiple) — runs the actual DepthCaches via UBLDC

Each DCN runs a single Python process, so **one DCN per CPU core** gives the best performance (Python's GIL limits 
each process to one core).

| Setup | Example configuration |
|-------|----------------------|
| Local (8-core PC) | 1 mgmt, 1 restapi, 6 DCN processes |
| Kubernetes (2 servers, 4 cores each) | 1 mgmt, 3 restapi, 4 DCN pods |

When you create DepthCaches (e.g. 200 markets with `desired_quantity=2`), UBDCC distributes them evenly across DCN 
processes. Each DCN downloads order book snapshots using its own network connection. Replicas are created for 
redundancy — if one DCN goes down, the other copy keeps serving data.

[![Visual overview](https://lucid.app/publicSegments/view/7ba7d734-4bb2-467f-b7b9-74ea0d1deec2/image.png)](https://lucid.app/publicSegments/view/7ba7d734-4bb2-467f-b7b9-74ea0d1deec2/image.png)

## Key Features

- **Fast access**: Order book data in ~3ms (cluster-internal) or ~4ms total request time on local networks. Over the 
internet typically ~60ms. All requests are load-balanced with automatic failover across redundant DepthCache copies.
- **Any language**: Retrieve DepthCache data via HTTP/JSON from any programming language. Python users can use the 
[UBLDC cluster module](https://oliver-zehentleitner.github.io/unicorn-binance-local-depth-cache/unicorn_binance_local_depth_cache.html#module-unicorn_binance_local_depth_cache.cluster) 
for sync and async access.
- **Flexible filtering**: Trim data at the cluster level — limit to top N Asks/Bids or filter by volume threshold. 
No need to transfer the full order book when you only need the best prices.
- **Compiled C-Extensions**: The entire cluster runs as Cython-compiled code for maximum performance.
- **Smart rate limiting**: Automatically throttles initialization when Binance API weight costs get too high.
- **Self-healing state**: The cluster database is replicated to every node on each sync cycle. If the management pod 
restarts, it automatically recovers the latest state from the node with the most recent backup — no external database 
(Redis, etcd) required, zero manual intervention.
- **Full transparency**: Every request can include `debug=true` to get detailed timing breakdowns 
(cluster execution time, transmission time, total request time), the internal routing URL, and which pods handled the 
request.
- **Supported exchanges**:

| Exchange                                                           | Exchange string               | 
|--------------------------------------------------------------------|-------------------------------| 
| [Binance](https://www.binance.com)                                 | `binance.com`                 |
| [Binance Testnet](https://testnet.binance.vision/)                 | `binance.com-testnet`         |
| [Binance USD-M Futures](https://www.binance.com)                   | `binance.com-futures`         |
| [Binance USD-M Futures Testnet](https://testnet.binancefuture.com) | `binance.com-futures-testnet` |
| [Binance US](https://www.binance.us/)                              | `binance.us`                  |
| [Binance TR](https://www.trbinance.com)                            | `trbinance.com`               |

If you like the project, please 
[![star](https://raw.githubusercontent.com/oliver-zehentleitner/unicorn-binance-local-depth-cache/master/images/misc/star.png)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/stargazers) it on 
[GitHub](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster)! 

## Local Setup (without Kubernetes)

Run UBDCC on a single machine — useful for development, backtesting, or when you need multiple bots to share the same 
DepthCache data without duplicate WebSocket connections.

### Install

```bash
pip install ubdcc-mgmt ubdcc-restapi ubdcc-dcn
```

### Start the components

Open a separate terminal for each process:

```bash
# Terminal 1: Management (internal, port 42080)
python -c "import os; from ubdcc_mgmt.Mgmt import Mgmt; Mgmt(cwd=os.getcwd())"

# Terminal 2: REST API (your access point, port 42081)
python -c "import os; from ubdcc_restapi.RestApi import RestApi; RestApi(cwd=os.getcwd())"

# Terminal 3+: DepthCacheNode (start one per CPU core you want to use)
python -c "import os; from ubdcc_dcn.DepthCacheNode import DepthCacheNode; DepthCacheNode(cwd=os.getcwd())"
```

**Start order does not matter.** All components automatically discover each other and reconnect if any process 
restarts. The mgmt needs a few seconds on first start before it accepts registrations.

### Ports

| Component | Default port | Purpose |
|-----------|-------------|---------|
| mgmt | 42080 | Internal cluster management (not for direct use) |
| restapi | 42081 | **Your access point** — all queries go here |
| dcn | 42082+ | Internal, auto-increments if multiple DCNs run on the same host |

### Good to know

- **DCN ports auto-increment**: When you start multiple DCN processes on the same machine, each one automatically 
finds the next free port (42082, 42083, 42084, ...). No manual configuration needed.
- **DepthCaches need a moment**: After creating a DepthCache, it needs a few seconds to download the initial order 
book snapshot from Binance before it can serve data. The status changes from `starting` to `running`.
- **Initialization is sequential**: DepthCaches are initialized one by one to stay within Binance API rate limits. 
This is slower at startup but ensures stable operation. With redundancy (`desired_quantity > 1`), the delay is not 
noticeable in production because at least one copy is always running.

## REST API

The REST API (default port **42081** locally, port **80** on Kubernetes) provides the following endpoints:

### Create DepthCaches

```bash
# Create multiple DepthCaches (POST with JSON body)
curl -X POST 'http://127.0.0.1:42081/create_depthcaches' \
  -H 'Content-Type: application/json' \
  -d '{"exchange": "binance.com", "markets": ["BTCUSDT", "ETHUSDT", "BNBUSDT"], "desired_quantity": 2}'

# Create a single DepthCache (GET)
curl 'http://127.0.0.1:42081/create_depthcache?exchange=binance.com&market=BTCUSDT&desired_quantity=2'

# Create multiple via GET (useful for browser testing, comma-separated markets)
curl 'http://127.0.0.1:42081/create_depthcaches?exchange=binance.com&markets=BTCUSDT,ETHUSDT&desired_quantity=1'
```

### Query order book data

```bash
# Get top 3 asks
curl 'http://127.0.0.1:42081/get_asks?exchange=binance.com&market=BTCUSDT&limit_count=3'

# Get bids filtered by volume threshold
curl 'http://127.0.0.1:42081/get_bids?exchange=binance.com&market=ETHUSDT&threshold_volume=100000'
```

### Manage and monitor

```bash
# List all DepthCaches and their status
curl 'http://127.0.0.1:42081/get_depthcache_list'

# Get detailed info for a specific DepthCache
curl 'http://127.0.0.1:42081/get_depthcache_info?exchange=binance.com&market=BTCUSDT'

# Cluster overview (registered pods, versions, timestamps)
curl 'http://127.0.0.1:42081/get_cluster_info'

# Stop a DepthCache
curl 'http://127.0.0.1:42081/stop_depthcache?exchange=binance.com&market=BTCUSDT'
```

### Debugging

Add `debug=true` to any request to get timing and routing details:

```bash
curl 'http://127.0.0.1:42081/get_asks?exchange=binance.com&market=BTCUSDT&limit_count=2&debug=true'
```

The response includes a `debug` block with:
- `cluster_execution_time` — time spent processing the request inside the cluster
- `transmission_time` — network overhead between restapi and DCN
- `request_time` — total round-trip time (filled by the UBLDC Python client)
- `url` — the internal URL that was routed to
- `post_body` — the POST body (for POST requests)
- `used_pods` — which pods handled this request

## Kubernetes Setup

- Get a Kubernetes cluster with powerful CPUs from a provider of your choice and connect `kubectl`
- Install dependencies

```
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### Helm Chart
- [Install Helm](https://helm.sh/docs/intro/install) 
- Prepare `helm`

``` 
helm repo add ubdcc https://oliver-zehentleitner.github.io/unicorn-binance-depth-cache-cluster/helm
helm repo update
```

- Install the UNICORN Binance DepthCache Cluster

``` 
helm install ubdcc ubdcc/ubdcc
```

- Get the "LoadBalancer Ingress" IP, the default Port is TCP 80!

```
kubectl describe services ubdcc-restapi
```

#### Choose an explicit version
- Find a version to choose

``` 
helm search repo ubdcc
```

- Then

``` 
helm install ubdcc ubdcc/ubdcc --version 0.2.0
```

#### Choose a namespace
``` 
helm install ubdcc ubdcc/ubdcc --namespace ubdcc
```

#### Choose an alternate public port
``` 
helm install ubdcc ubdcc/ubdcc --set publicPort.restapi=8080
```
  
### Kubernetes Deployment
- [Download the deployment files](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/tree/master/admin/k8s)
- Apply the deployment files with `kubectl`

``` 
kubectl apply -f ./setup/01_namespace_ubdcc.yaml
kubectl apply -f ./setup/02_role_ubdcc.yaml
kubectl apply -f ./setup/03_rolebinding_ubdcc.yaml
kubectl apply -f ./ubdcc-dcn.yaml  
kubectl apply -f ./ubdcc-mgmt.yaml
kubectl apply -f ./ubdcc-mgmt_service.yaml
kubectl apply -f ./ubdcc-restapi.yaml
kubectl apply -f ./ubdcc-restapi_service.yaml
```

- Get the "LoadBalancer Ingress" IP, the default Port is TCP 80:

```
kubectl describe services ubdcc-restapi
```

## Security
In any case, you should set the firewall in the web interface of the Kubernetes provider so that only your systems 
have access to UBDCC.

If you want to do this, you can add HTTPS to the LoadBalancer with most providers.
  
## Uninstallation
```
kubectl delete -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### Helm Chart
```
helm uninstall ubdcc
```

### Kubernetes Deployment
- Delete the deployment with `kubectl`

``` 
kubectl delete -f ./setup/01_namespace_ubdcc.yaml
kubectl delete -f ./setup/02_role_ubdcc.yaml
kubectl delete -f ./setup/03_rolebinding_ubdcc.yaml
kubectl delete -f ./ubdcc-dcn.yaml  
kubectl delete -f ./ubdcc-mgmt.yaml
kubectl delete -f ./ubdcc-mgmt_service.yaml
kubectl delete -f ./ubdcc-restapi.yaml
kubectl delete -f ./ubdcc-restapi_service.yaml
```

## Accessing from Python

While the REST API can be used from any language, Python users can use the 
[UBLDC cluster module](https://github.com/oliver-zehentleitner/unicorn-binance-local-depth-cache?tab=readme-ov-file#connect-to-a-unicorn-binance-depth-cache-cluster) 
for a native experience with sync and async support, automatic connection handling, and `debug=True` output.

See the [examples](https://github.com/oliver-zehentleitner/unicorn-binance-local-depth-cache/tree/master/examples/unicorn_binance_depth_cache_cluster).

## How to report Bugs or suggest Improvements?
[List of planned features](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement) - click ![thumbs-up](https://raw.githubusercontent.com/oliver-zehentleitner/unicorn-binance-suite/master/images/misc/thumbup.png) if you need one of them or suggest a new feature!

Before you report a bug, [try the latest release](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster#installation-and-upgrade). If the issue still exists, provide the error trace, OS 
and Python version and explain how to reproduce the error. A demo script is appreciated.

If you don't find an issue related to your topic, please open a new [issue](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/issues)!

[Report a security bug!](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/security/policy)

## Contributing
[UNICORN Binance DepthCache Cluster](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster) is an open 
source project which welcomes contributions which can be anything from simple documentation fixes and reporting dead links to new features. To 
contribute follow 
[this guide](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/blob/master/CONTRIBUTING.md).
 
### Contributors
[![Contributors](https://contributors-img.web.app/image?repo=oliver-zehentleitner/unicorn-binance-depth-cache-cluster)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/graphs/contributors)

We ![love](https://raw.githubusercontent.com/oliver-zehentleitner/unicorn-binance-suite/master/images/misc/heart.png) open source!

## Disclaimer
This project is for informational purposes only. You should not construe this information or any other material as 
legal, tax, investment, financial or other advice. Nothing contained herein constitutes a solicitation, recommendation, 
endorsement or offer by us or any third party provider to buy or sell any securities or other financial instruments in 
this or any other jurisdiction in which such solicitation or offer would be unlawful under the securities laws of such 
jurisdiction.

### If you intend to use real money, use it at your own risk!

Under no circumstances will we be responsible or liable for any claims, damages, losses, expenses, costs or liabilities 
of any kind, including but not limited to direct or indirect damages for loss of profits.
