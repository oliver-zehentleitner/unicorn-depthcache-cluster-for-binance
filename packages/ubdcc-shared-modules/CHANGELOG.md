# ubdcc-shared-modules Change Log

All notable changes to this package will be documented in this file.

## 0.3.0.dev (development stage/unreleased/unstable)
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
