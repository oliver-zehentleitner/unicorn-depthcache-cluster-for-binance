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

Scalable, redundant order book data for Binance — deployed on Kubernetes, accessed via REST API from any language.

Built on [UNICORN Binance Local Depth Cache (UBLDC)](https://github.com/oliver-zehentleitner/unicorn-binance-local-depth-cache). 
Part of the [UNICORN Binance Suite](https://github.com/oliver-zehentleitner/unicorn-binance-suite).

## Why?

Running order book depth caches on a single machine hits limits fast:

- **Rate limits**: One public IP can only handle so many Binance API requests. A cluster spreads the load across 
multiple nodes with their own IPs.
- **Shared access**: Multiple trading bots, services or team members need the same order book data. UBDCC serves it 
via a REST API — no shared state, no duplicate connections.
- **Reliability**: If a node goes down, redundant copies of each DepthCache keep serving data. The management pod 
recovers its state automatically from the remaining nodes.

## How it works

Deploy UBDCC on a Kubernetes cluster and create DepthCaches through the REST API instead of running them locally.

The cluster consists of three pod types:
- **mgmt** (1x) — manages the cluster state, distributes DepthCaches across nodes
- **restapi** (1x per node) — REST API gateway, load-balances requests to DCN pods
- **dcn** (multiple) — runs the actual DepthCaches via UBLDC

Each DCN pod runs a single Python process, so **one DCN pod per CPU core** gives the best performance (Python's GIL 
limits each process to one core). A typical setup with 2 servers and 4 cores each: 1 mgmt, 2 restapi, 6 DCN pods.

For example, when you configure the system to create 200 DepthCaches with a `desired_quantity` of `2`, UBDCC will deploy
2 DepthCaches for each symbol/market. These are evenly distributed across the DCN pods and can download order book 
snapshots from the Binance REST API using their own public IP addresses. On the first run, each pod starts its share of 
DepthCaches as quickly as possible. Afterward, replicas are initiated for redundancy.

[![Visual overview](https://lucid.app/publicSegments/view/7ba7d734-4bb2-467f-b7b9-74ea0d1deec2/image.png)](https://lucid.app/publicSegments/view/7ba7d734-4bb2-467f-b7b9-74ea0d1deec2/image.png)

## Key Features

- **Fast access**: Order book Asks/Bids in ~0.01s (local) or ~0.06s (internet). All requests are load-balanced with 
automatic failover.
- **Any language**: Retrieve DepthCache data via HTTP/JSON. Python users can use the 
[UBLDC cluster module](https://oliver-zehentleitner.github.io/unicorn-binance-local-depth-cache/unicorn_binance_local_depth_cache.html#module-unicorn_binance_local_depth_cache.cluster) 
for sync and async access.
- **Flexible filtering**: Trim data at the cluster level — limit to top N Asks/Bids or filter by volume threshold.
- **Compiled C-Extensions**: The entire cluster runs as Cython-compiled code for maximum performance.
- **Smart rate limiting**: Automatically throttles initialization when Binance API weight costs get too high.
- **Self-healing state**: The cluster database is replicated to every node. If the management pod restarts, it 
recovers the latest state automatically — no external database (Redis, etcd) required.
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

## Installation

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

## Accessing the DepthCaches

The UNICORN Binance DepthCache Cluster is accessed with the Python module [UNICORN Binance Local Depth Cache](https://github.com/oliver-zehentleitner/unicorn-binance-local-depth-cache?tab=readme-ov-file#connect-to-a-unicorn-binance-depth-cache-cluster).

Just try this [examples](https://github.com/oliver-zehentleitner/unicorn-binance-local-depth-cache/tree/master/examples/unicorn_binance_depth_cache_cluster)!

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
