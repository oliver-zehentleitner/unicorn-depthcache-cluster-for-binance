# TASKS.md — UNICORN DepthCache Cluster for Binance

Open development tasks, ideas, and decisions.

---

## In Progress

*(none)*

---

## Backlog

### [ ] Set up Docker registry and update build scripts
- OVH private registry is gone with LUCIT
- Decision needed: GitHub Container Registry (ghcr.io) or Docker Hub
- Update all `dev/docker/*.sh` scripts and Dockerfiles with new registry

### [ ] Regenerate Sphinx HTML docs
- Theme changed from `python_docs_theme_lucit` to `alabaster`
- All `docs/` HTML files still reference old LUCIT theme and package names
- Run `cd dev/sphinx && make html` after Sphinx environment setup

### [ ] Add unit tests
- No test coverage exists at all
- Start with mocked unit tests for `Database.py` and `App.py` logic

### [ ] Audit and fix all silent except/pass blocks
- Suite-wide initiative — same task tracked in all unicorn-* repos


---

## Done

### [x] Remove LUCIT licensing system
- Deleted `LicensingManager.py` and `LicensingExceptions.py`
- Removed all license checks from `App.py`, `Database.py`, `RestEndpointsBase.py`
- Removed `submit_license` endpoints from mgmt and restapi
- Removed license params from UBLDC instantiation in DCN
- Removed `lucit-licensing-python` from all setup.py and pyproject.toml

### [x] Fix deprecated UBLDC method call in DepthCacheNode.py
- `create_depth_cache()` → `create_depthcache()` in DCN

### [x] Pin UBLDC dependency to current stable version
- `ubdcc-dcn` setup.py: `unicorn_binance_local_depth_cache==2.6.0` → `unicorn-binance-local-depth-cache>=2.8.1`

### [x] Rebrand LUCIT → Oliver Zehentleitner / MIT
- Renamed packages: `lucit-ubdcc-*` → `ubdcc-*`, namespaces: `lucit_ubdcc_*` → `ubdcc_*`
- Replaced LSOSL with MIT license
- Updated all headers, copyright, author, URLs
- Updated K8s, Helm, Docker, CI/CD, Sphinx
