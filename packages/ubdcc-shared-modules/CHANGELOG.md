# ubdcc-shared-modules Change Log

All notable changes to this package will be documented in this file.

## 0.7.1.dev (development stage/unreleased/unstable)

## 0.7.1
### Changed
- **`App.py`: default log level is now `ERROR` (was `DEBUG`).** Cuts
  per-tick disk noise so production deployments don't fill the log
  directory. Override with the new `log_level` kwarg on `App()` or via
  `ServiceBase` subclasses (`Mgmt`, `RestApi`, `DepthCacheNode`).
### Added
- `App.__init__` and `ServiceBase.__init__` accept a `log_level` kwarg
  (str: `DEBUG|INFO|WARNING|ERROR|CRITICAL`, or any `logging.*` int).
  When `None`, falls back to the new `ERROR` default.

## 0.7.0
### Fixed
- `AccountGroups.py`: added `binance.com-margin-testnet` and
  `binance.com-isolated_margin-testnet` to the
  `EXCHANGE_TO_ACCOUNT_GROUP` map, both routed to
  `binance.com-testnet` (they share the `testnet.binance.vision`
  account). Without this, `get_account_group()` returned `None` for
  testnet-margin DCNs.

## 0.6.0
### Added
- `Database.rebalance_account_group(account_group)`: redistributes every
  active DCN uid (`ROLE=ubdcc-dcn`) round-robin across the credentials
  available for the given account group. Called from
  `add_credentials()`, `delete_credentials()`, and from `revise()` via
  the new `rebalance_credential_assignments_if_needed()` whenever the
  DCN population changes. Replaces the previous lazy "first caller gets
  assigned on request" semantics that left `assigned_dcns: []` after
  any transient `None` return.

## 0.5.0
### Changed
- `AccountGroups`: `binance.com-vanilla-options` now resolves to the
  `binance.com` account group; `binance.com-vanilla-options-testnet`
  resolves to `binance.com-futures-testnet`. Vanilla-options depth
  caches share the same credential pool as their underlying exchange.

## 0.4.0
### Changed
- `get_ok_response()` now accepts optional `error` and `error_id` parameters, matching the existing error-response convention. Enables OK-with-warnings responses (e.g. failover success in restapi).
### Added
- `Database`: `LAST_DISTRIBUTION_CHANGE` + `DISTRIBUTION_CHANGES` fields per DepthCache, auto-incremented on add/delete distribution. `RESTARTS` counter per distribution entry, incremented when `update_depthcache_distribution(last_restart_time=...)` advances the timestamp.

## 0.3.0
### Added
- `/shutdown` REST endpoint (dev-mode only) on all pods — triggers graceful process shutdown via REST
- `mgmt_port` parameter on `App` and `ServiceBase` — allows custom mgmt port via CLI
- `post_body` field in `create_debug_response()` — POST body now visible in `debug=true` response
### Fixed
- `/shutdown` endpoint now force-exits via `os._exit(0)` 0.5s after the response — previously processes could hang if the main loop was stuck in `asyncio.sleep`
- `is_port_free()` now sets `SO_REUSEADDR` — TIME_WAIT state after a restart no longer blocks rebinding to the same port
- Port retry on bind failure — `start_rest_server()` checks if the uvicorn thread is alive and tries the next port if not (fixes race condition when multiple DCNs start simultaneously)
- Removed orphaned `except AttributeError` block leftover from LUCIT removal that caused Cython build failure
### Changed
- Python support extended to 3.9-3.14 on Linux, macOS and Windows
- Replaced `json` with `orjson` for faster JSON parsing
- Build workflow: migrated to UBWA pattern (3 OS matrix, cibuildwheel v3.4.1, sdist, GitHub Release)

## 0.2.0
### Changed
- Rebranded from LUCIT to open source MIT
- Renamed: `lucit-ubdcc-shared-modules` → `ubdcc-shared-modules`, namespace `lucit_ubdcc_shared_modules` → `ubdcc_shared_modules`
- LICENSE: LSOSL → MIT
- Author: LUCIT Systems and Development → Oliver Zehentleitner
### Removed
- LUCIT licensing system (`LicensingManager`, `LicensingExceptions`)
- `lucit-licensing-python` dependency
