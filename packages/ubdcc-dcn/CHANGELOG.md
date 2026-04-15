# ubdcc-dcn Change Log

All notable changes to this package will be documented in this file.

## 0.3.0.dev (development stage/unreleased/unstable)
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
