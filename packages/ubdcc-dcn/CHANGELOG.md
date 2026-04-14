# ubdcc-dcn Change Log

All notable changes to this package will be documented in this file.

## 0.2.1
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
