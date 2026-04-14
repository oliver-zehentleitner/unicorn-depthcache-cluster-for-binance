# UNICORN Binance DepthCache Cluster (ubdcc) Change Log

All notable changes to this package will be documented in this file.

## 0.2.1
### Added
- `ubdcc` CLI cluster manager with interactive console:
  - `ubdcc start --dcn N [--port PORT] [--logdir DIR]` — spawn mgmt, restapi and N DCN processes
  - `ubdcc status` — show all pods with role, name, port, status and version
  - `ubdcc stop` — graceful shutdown of the entire cluster
  - `ubdcc restart <name>` — full restart (shutdown + respawn) for mgmt, restapi or DCN
  - Interactive `ubdcc>` prompt during `start`:
    - `add-dcn [count]` — spawn new DCN process(es)
    - `remove-dcn <count|name>` — stop DCN(s) by count or name
    - `status`, `restart <name>`, `stop`, `help`
- `python -m ubdcc` entry point for running from source during development
- `.ubdcc` state file for automatic port detection across CLI commands
- `--help` epilog listing all interactive shell commands
- GitHub Release step in the build workflow
### Changed
- Python support extended to 3.9-3.14 on Linux, macOS and Windows
- Workflow renamed to "Build and Publish GH+PyPi (ubdcc)" for consistency with other packages

## 0.2.0
### Added
- Initial release as meta-package and cluster manager stub
- Installs all UBDCC components: ubdcc-mgmt, ubdcc-restapi, ubdcc-dcn
