# unicorn-binance-depth-cache-cluster Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to 
[Semantic Versioning](http://semver.org/).

[Discussions about unicorn-binance-depth-cache-cluster releases!](https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/discussions/categories/releases)

[How to upgrade to the latest version!](https://oliver-zehentleitner.github.io/unicorn-binance-depth-cache-cluster/readme.html#installation-and-upgrade)

## 0.5.0.dev (development stage/unreleased/unstable)
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
- CLI `status`: show UBLDC version in parentheses next to each DCN's version
- CLI `status`: DepthCache redundancy summary — replica breakdown (running/starting) and redundancy categories (fully redundant, degraded, no redundancy)
- AccountGroups: `binance.com-vanilla-options` → `binance.com`, `binance.com-vanilla-options-testnet` → `binance.com-futures-testnet`

## 0.4.1
### Fixed
- Compiled file 'ubdcc_shared_modules.AccountGroups' was missing in the wheels
- Pinning ubdcc versions in ubdcc cli requirements

## 0.4.0
### Added
- Binance API credentials support. Optional: add one or more `(api_key, api_secret)` pairs per account group (`binance.com`, `binance.com-testnet`, `binance.com-futures-testnet`, `binance.us`, `binance.tr`) via new REST endpoints `/ubdcc_add_credentials` (POST/GET), `/ubdcc_remove_credentials`, `/ubdcc_get_credentials_list` and matching `ubdcc credentials add/list/remove` CLI subcommands. Mgmt load-balances credentials across DCN pods (fewest-assigned-first); DCNs fetch their assigned key via the internal `/ubdcc_assign_credentials` endpoint and pass it to UBLDC as a `BinanceRestApiManager`. Lets the cluster use authenticated rate limits without mandating credentials — public-only operation remains unchanged. Keys are part of the self-healing DB sync (full cleartext cluster-internal); public responses only show masked previews and the list of assigned DCN UIDs per key. See README → API Credentials for the security trade-offs.
- `get_asks` / `get_bids`: when failover recovers from one or more unreachable DCNs, the successful response now includes an `error_id` (`#5001`) and an `error` message listing the pods that failed before success. Gives monitoring a visible signal that failover occurred without changing the OK-with-data semantics. Closes #3.
- DepthCache distribution tracking: new DB fields `LAST_DISTRIBUTION_CHANGE` + `DISTRIBUTION_CHANGES` (top-level, counts how often a DC has been re-assigned across pods) and `RESTARTS` per distribution entry (counts stream restarts on the currently assigned pod). Visible in `get_depthcache_info` / `get_depthcache_list` — useful for diagnosing upstream stability and cluster rebalancing history. Closes #1.
### Removed
- External `ubdcc restart <name>` CLI subcommand — it didn'''t actually work because the spawn functions live in the interactive shell closure. Restart is still available inside the interactive `ubdcc>` shell.
### Fixed
- DCN startup crash: `self._restart_queue` was initialized *after* `super().__init__()`, but `ServiceBase.__init__()` blocks on `self.app.start()` and runs `main()` synchronously — so the assignment was never reached. Every DCN crashed seconds after registering with `AttributeError: '_restart_queue'`, leaving only mgmt and restapi alive. Queue init now runs before `super().__init__()`.

## 0.3.3
### Added
- New `ubdcc` meta-package and cluster manager (`pip install ubdcc`)
- `ubdcc` CLI command with interactive console:
  - `ubdcc start --dcn 4` — starts mgmt, restapi and DCN processes
  - `ubdcc status` — shows all pods with role, name, port, status
  - `ubdcc stop` — graceful shutdown via REST
  - `ubdcc restart <name>` — full restart (shutdown + respawn) for mgmt, restapi or DCN
  - `add-dcn [count]` — spawn new DCN process(es) from the interactive shell
  - `remove-dcn <count|name>` — stop DCN(s) by count or by name
  - Interactive `ubdcc>` prompt during `start` for live management
  - `python -m ubdcc` entry point for running from source during development
- `/shutdown` REST endpoint on all pods (dev-mode only) for graceful process shutdown
- `/create_depthcaches` now supports both GET (comma-separated markets) and POST (JSON body)
- `mgmt_port` parameter on all services — allows custom port configuration via CLI
- `.ubdcc` state file for automatic port detection across CLI commands
- `debug=true` now includes `post_body` in response for POST requests
- Port retry on bind failure — fixes race condition when multiple DCNs start simultaneously
- Mermaid architecture diagram in README (replaces external Lucidchart image)
- Comprehensive README rewrite: What is UBDCC, Why, Architecture, Local Setup, REST API reference with all endpoints, debugging guide
- Python 3.9-3.14 support on Linux, macOS and Windows (all 5 packages)
- Build workflows updated to UBWA pattern: 3 OS matrix, cibuildwheel v3.4.1, sdist, GitHub Release
- New build workflow for `ubdcc` package (pure Python)
### Changed
- Replaced `json` with `orjson` for faster JSON parsing (closes #5)
- `/create_depthcaches` switched from GET to POST as primary method (closes #10)
- Build target: Python 3.14 only → Python 3.9-3.14 on all platforms
- Aligned `project_urls` across all packages with UBS standard
### Fixed
- Remove remaining LUCIT references in issue templates, PR template, container LICENSE files, container READMEs, dev scripts
- Fix issue templates: correct project name, add Python 3.13/3.14 to dropdown
- Fix README: wrong port (42080 → 42081), old project name, typos
- Fix double JSON serialization in UBLDC cluster POST requests
- `/shutdown` endpoint now force-exits via `os._exit(0)` 0.5s after the response — previously processes could hang if the main loop was stuck in `asyncio.sleep`
- `is_port_free()` now sets `SO_REUSEADDR` — previously the TIME_WAIT state after a restart caused the new mgmt to land on the next port, breaking restapi/DCN connections
### Removed
- License purchase and commercial support sections from all package READMEs
- External Lucidchart dependency (replaced with inline Mermaid diagram)

## 0.2.0
### Added
- AGENTS.md and TASKS.md
### Changed
- Rebranded from LUCIT to open source MIT
- Renamed packages: `lucit-ubdcc-*` → `ubdcc-*`, namespaces: `lucit_ubdcc_*` → `ubdcc_*`
- Kubernetes namespace: `lucit-ubdcc` → `ubdcc`
- LICENSE: LSOSL → MIT
- Author: LUCIT Systems and Development → Oliver Zehentleitner
- All URLs updated from lucit.tech/shop.lucit.services to GitHub
- Sphinx docs theme: `python_docs_theme_lucit` → `alabaster`
### Fixed
- `create_depth_cache()` → `create_depthcache()` in `DepthCacheNode.py` (deprecated method call)
- Per-package LICENSE files replaced with correct MIT license
- Remaining LUCIT references in file headers, pyproject.toml descriptions, and per-package CHANGELOGs
- UBLDC dependency pin: `unicorn_binance_local_depth_cache==2.6.0` → `unicorn-binance-local-depth-cache>=2.8.1`
### Removed
- LUCIT licensing system (LicensingManager, LicensingExceptions, submit_license endpoints)
- `lucit-licensing-python` dependency from all packages
- License params (`lucit_api_secret`, `lucit_license_token`) from UBLDC instantiation in DCN

## 0.1.4
### Fixed
- https://github.com/oliver-zehentleitner/unicorn-binance-depth-cache-cluster/issues/8 - We don't overwrite 
  the None anymore.

## 0.1.3
MVP release!