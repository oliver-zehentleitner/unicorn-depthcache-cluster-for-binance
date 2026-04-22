# UNICORN Binance DepthCache Cluster (ubdcc) Change Log

All notable changes to this package will be documented in this file.

## 0.6.0.dev (development stage/unreleased/unstable)
### Changed
- CLI `status`: redundancy summary split into clearer categories.
  Previously a DepthCache with `desired=1, running=0` was reported as
  "no redundancy" and `desired>=2, running=0` as "degraded", hiding the
  fact that the cache was completely down. Now:
  - `unavailable` — desired > 0 but nothing running
  - `no redundancy` — desired = 1, running = 1
  - `degraded` — desired >= 2, 0 < running < desired
  - `fully redundant` — desired >= 2, running >= desired
  - `inactive` — desired = 0 (only shown when non-zero)

## 0.6.0
### Added
- CLI `status`: new "DC restarts" section lists every depth cache whose
  WebSocket stream has been restarted at least once, sorted by restart
  count descending, with a human-readable "last restart" timestamp
  (e.g. `45s ago`, `2h ago`). Hidden when no DC has restarted.
- CLI `--help`: the top-level help now lists the `credentials`
  subcommands (`add`, `remove`, `list`) in the epilog alongside the
  interactive shell commands, so users no longer need to run
  `ubdcc credentials --help` to discover them.

## 0.5.0
### Added
- CLI `status`: UBLDC version shown in parentheses next to each DCN's
  version.
- CLI `status`: DepthCache redundancy summary — replica breakdown
  (running/starting) and redundancy categories (fully redundant,
  degraded, no redundancy).

## 0.4.0
### Removed
- External `ubdcc restart <name>` CLI subcommand — only worked inside the interactive shell. The shell command is unchanged.

## 0.3.0
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
- Workflow renamed to "Build and Publish PyPi (ubdcc)" for consistency with other packages

## 0.2.0
### Added
- Initial release as meta-package and cluster manager stub
- Installs all UBDCC components: ubdcc-mgmt, ubdcc-restapi, ubdcc-dcn
