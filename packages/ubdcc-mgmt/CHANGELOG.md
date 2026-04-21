# ubdcc-mgmt Change Log

All notable changes to this package will be documented in this file.

## 0.6.0.dev (development stage/unreleased/unstable)

## 0.6.0
### Fixed
- `/ubdcc_update_depthcache_distribution` read `last_restart_time`
  from the query string but never forwarded it to
  `Database.update_depthcache_distribution()`, so the `RESTARTS`
  counter per distribution entry stayed at `0` forever regardless
  of how many stream restarts the DCNs reported. The handler also
  did not cast the query value from `str` to `float`, which would
  have caused a silent string-vs-float comparison in the DB layer.
  Both fixed: value is cast (with error response `#1024` on
  malformed input) and passed through to the DB call.

## 0.5.0

## 0.4.0

## 0.3.0
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
