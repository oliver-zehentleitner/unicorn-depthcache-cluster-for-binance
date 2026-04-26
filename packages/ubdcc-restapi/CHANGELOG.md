# ubdcc-restapi Change Log

All notable changes to this package will be documented in this file.

## 0.8.0.dev (development stage/unreleased/unstable)

## 0.7.0
### Changed
- **Breaking**: renamed the three user-facing credential endpoints —
  `/ubdcc_add_credentials` → `/add_credentials`,
  `/ubdcc_remove_credentials` → `/remove_credentials`,
  `/ubdcc_get_credentials_list` → `/get_credentials_list`.
  restapi proxies them to mgmt as before; proxy target paths on mgmt
  renamed in sync.

## 0.6.0

## 0.5.0

## 0.4.0
### Added
- Failover visibility: when `/get_asks` or `/get_bids` recovers from one or more DCN failures, the response stays `result: OK` with data as before, but additionally carries `error_id: "#5001"` and an `error` string listing the failed pods. Gives clients a monitoring hook for partial-failure events.

## 0.3.0
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
