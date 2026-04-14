[![GitHub Release](https://img.shields.io/github/release/oliver-zehentleitner/unicorn-binance-depth-cache-cluster.svg?label=github)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/releases)
[![GitHub Downloads](https://img.shields.io/github/downloads/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/total?color=blue)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/releases)
[![PyPi Release](https://img.shields.io/pypi/v/ubdcc?color=blue)](https://pypi.org/project/ubdcc/)
[![PyPi Downloads](https://pepy.tech/badge/ubdcc)](https://pepy.tech/project/ubdcc)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://oliver-zehentleitner.github.io/unicorn-binance-depth-cache-cluster/license.html)
[![Supported Python Version](https://img.shields.io/pypi/pyversions/ubdcc.svg)](https://www.python.org/downloads/)
[![PyPI - Status](https://img.shields.io/pypi/status/ubdcc.svg)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/issues)
[![Build and Publish PyPi](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/actions/workflows/build_wheels_ubdcc.yml/badge.svg)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/actions/workflows/build_wheels_ubdcc.yml)
[![Read the Docs](https://img.shields.io/badge/read-%20docs-yellow)](https://oliver-zehentleitner.github.io/unicorn-binance-depth-cache-cluster)
[![Github](https://img.shields.io/badge/source-github-cbc2c8)](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/tree/master/packages/ubdcc)
[![Telegram](https://img.shields.io/badge/community-telegram-41ab8c)](https://t.me/unicorndevs)
[![Gitter](https://img.shields.io/badge/community-gitter-41ab8c)](https://gitter.im/unicorn-trading-suite/unicorn-binance-depth-cache-cluster?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# UNICORN Binance DepthCache Cluster

The `ubdcc` package is the all-in-one installer and cluster manager for the 
[UNICORN Binance DepthCache Cluster](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster).

## What you get

- **All components installed**: `ubdcc-mgmt`, `ubdcc-restapi`, `ubdcc-dcn` and their dependencies
- **`ubdcc` command**: Cluster manager to start, stop and monitor your UBDCC instance (work in progress)

## Quick Start

```bash
pip install ubdcc
```

This installs everything you need. Start the cluster:

```bash
ubdcc start --dcn 4
```

This starts 1 mgmt + 1 restapi + 4 DCN processes and drops you into an interactive console where you can monitor 
and manage the cluster (`status`, `stop`, `restart <name>`, `help`).

The REST API is available at `http://127.0.0.1:42081/`.

### Development (without pip install)

When working on the source code, run directly from the package directory:

```bash
cd packages/ubdcc
python -m ubdcc start --dcn 4
python -m ubdcc status
python -m ubdcc stop
```

For full documentation, architecture overview, REST API reference and Kubernetes setup, see the 
[main project README](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster).

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
