# ubdcc-restapi Change Log

All notable changes to this package will be documented in this file.

## 0.2.1
### Added
- `/create_depthcaches` now supports both POST (JSON body, primary) and GET (query params, for browser debugging)
- `mgmt_port` parameter on `RestApi` — accepts custom port from the ubdcc CLI
- POST body is now included in `debug=true` response (`post_body` field)
### Changed
- Python support extended to 3.9-3.14 on Linux, macOS and Windows
- Replaced `json` with `orjson` for faster JSON parsing
- `/create_depthcaches` switched from GET to POST as primary method — forwards request body as-is to mgmt
- Build workflow: migrated to UBWA pattern (3 OS matrix, cibuildwheel v3.4.1, sdist, GitHub Release)

## 0.2.0
### Changed
- Rebranded from LUCIT to open source MIT
- Renamed: `lucit-ubdcc-restapi` → `ubdcc-restapi`, namespace `lucit_ubdcc_restapi` → `ubdcc_restapi`
- LICENSE: LSOSL → MIT
- Author: LUCIT Systems and Development → Oliver Zehentleitner
### Removed
- `submit_license` endpoint (LUCIT licensing system)
