# ubdcc-mgmt Change Log

All notable changes to this package will be documented in this file.

## 0.2.1
### Added
- `/create_depthcaches` now supports both POST (JSON body, primary) and GET (base64-encoded markets, for browser debugging)
- `mgmt_port` parameter on `Mgmt` — accepts custom port from the ubdcc CLI
### Fixed
- Remove double `import base64` that was left over after the orjson migration
### Changed
- Python support extended to 3.9-3.14 on Linux, macOS and Windows
- Replaced `json` with `orjson` for faster JSON parsing (closes #5)
- `/create_depthcaches` switched from GET to POST as primary method (closes #10) — prevents URL-too-long errors when creating many DepthCaches at once
- Build workflow: migrated to UBWA pattern (3 OS matrix, cibuildwheel v3.4.1, sdist, GitHub Release)

## 0.2.0
### Changed
- Rebranded from LUCIT to open source MIT
- Renamed: `lucit-ubdcc-mgmt` → `ubdcc-mgmt`, namespace `lucit_ubdcc_mgmt` → `ubdcc_mgmt`
- LICENSE: LSOSL → MIT
- Author: LUCIT Systems and Development → Oliver Zehentleitner
### Removed
- `submit_license` endpoint (LUCIT licensing system)
