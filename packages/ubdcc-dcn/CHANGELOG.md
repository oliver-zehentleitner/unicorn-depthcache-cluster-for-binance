# ubdcc-dcn Change Log

All notable changes to this package will be documented in this file.

## 0.8.0.dev (development stage/unreleased/unstable)

## 0.7.0
### Changed
- Bumped `unicorn-binance-local-depth-cache` minimum to `>=2.14.0`
  across `setup.py`, `requirements.txt` and `pyproject.toml`. The
  renamed cluster client credential methods live there (UBLDC 2.14.0
  also brings Binance Cross / Isolated Margin support end-to-end).

## 0.6.0
### Changed
- Credential handling moved from DCN-controlled to UBLDC-controlled.
  The DCN no longer constructs a `BinanceRestApiManager` itself —
  it only keeps a `credential_id_by_account_group` cache as a
  comparison reference. On every main-loop tick (and immediately
  after creating a fresh `BinanceLocalDepthCacheManager`),
  `_sync_credentials()` asks mgmt for the current assignment per
  used account group and, on an id diff, hot-swaps the UBRA inside
  every affected `BinanceLocalDepthCacheManager` via
  `ldc.set_credentials(api_key, api_secret)`. WebSocket streams keep
  running; new credentials take effect from the next REST call
  (initial snapshot / resync). Eliminates the previous "sticky `None`"
  cache bug that could leave `assigned_dcns: []` forever across DCN
  restarts.
- UBLDC dependency bumped: `>=2.11.0` → `>=2.13.0` in `setup.py`,
  `requirements.txt` and `pyproject.toml` (requires
  `BinanceLocalDepthCacheManager.set_credentials()`).

## 0.4.0
### Added
- Stream restart reporting: DCN registers an `on_restart` callback with each UBLDC instance. UBLDC invokes it from its manager thread when a stream restart is detected; DCN queues the event and the async main loop forwards it to mgmt via `ubdcc_update_depthcache_distribution(last_restart_time=...)`. Event-driven — no polling, no drift.
### Changed
- UBLDC dependency bumped: `>=2.8.1` → `>=2.11.0` (requires the `on_restart` callback).

## 0.3.0
### Added
- `mgmt_port` parameter on `DepthCacheNode` — accepts custom port from the ubdcc CLI
### Changed
- Python support extended to 3.9-3.14 on Linux, macOS and Windows
- Build workflow: migrated to UBWA pattern (3 OS matrix, cibuildwheel v3.4.1, sdist, GitHub Release)

## 0.2.0
### Changed
- Rebranded from LUCIT to open source MIT
- Renamed: `lucit-ubdcc-dcn` → `ubdcc-dcn`, namespace `lucit_ubdcc_dcn` → `ubdcc_dcn`
- LICENSE: LSOSL → MIT
- Author: LUCIT Systems and Development → Oliver Zehentleitner
### Fixed
- `create_depth_cache()` → `create_depthcache()` (deprecated UBLDC method call)
- UBLDC dependency: pinned `==2.6.0` → `>=2.8.1`
### Removed
- License params (`lucit_api_secret`, `lucit_license_token`) from UBLDC instantiation
