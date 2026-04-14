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

### [ ] Binance API Key support per DCN
- Currently all DCNs fetch order book snapshots without authentication (public rate limits)
- With API keys: higher rate limits → faster initialization with many DepthCaches
- Could pass api_key/api_secret per DCN or cluster-wide via CLI/config
- UBLDC already supports api_key/api_secret in BinanceLocalDepthCacheManager

### [ ] Audit and fix all silent except/pass blocks
- Suite-wide initiative — same task tracked in all unicorn-* repos

---

## Ideas — Distribution & Accessibility

UBDCC's core value is already accessible via 5 PyPI packages + REST API. These wrappers would lower the barrier 
further for different audiences.

### [ ] Docker Compose
- `docker compose up` → full cluster running
- Configurable DCN count via environment variable or compose profiles
- No K8s needed, familiar to most devs

### [ ] Docker Images on ghcr.io
- Public images at `ghcr.io/oliver-zehentleitner/ubdcc-*`
- Base image: `python:3.14-slim`
- GitHub Actions workflow for automated builds on release
- Decide: keep "-latest" variant or drop it
- Decide: amd64 only or also arm64

### [ ] Helm Chart update
- Already exists, needs registry URL update (OVH → ghcr.io)
- DCN: consider Deployment with configurable replicas instead of DaemonSet (1 per core, not 1 per node)

### [ ] Config file support (YAML/TOML)
- Predefined exchange, markets, ports, DCN count, desired_quantity
- Used by CLI tool and/or programmatic startup

### [ ] systemd service files
- For Linux server deployments without Docker/K8s
- Template-based: ubdcc-mgmt.service, ubdcc-restapi.service, ubdcc-dcn@.service (instanced)

### [ ] Web Dashboard
- Browser-based cluster monitoring and management
- Create/stop DepthCaches, view status, see performance metrics
- Higher effort, big wow-factor

### [ ] REST Client Libraries (JS, Go, C#, etc.)
- Generated from OpenAPI spec or hand-written thin wrappers
- Broadens the "any language" promise
- High effort per language

### Decision: Docker/K8s is deferred for 0.2.0
The 0.2.0 release ships with 5 PyPI packages + Local Setup + REST API documentation + CLI cluster manager.
Docker images, Helm chart update, and K8s deployment are a follow-up release.

---

## Ideas — Architecture

### [ ] DCN-local DB updates as distributed transaction log
**Status:** Concept only — needs visualization before implementation, easy to get wrong.

**Problem:** If mgmt crashes between a `create_depthcache`/`stop_depthcache` and the next node sync, the restored DB is missing that change. The gap is small but real.

**Concept:**
- Each DCN already holds a local copy of the mgmt DB (`ubdcc_mgmt_backup`)
- When a DCN successfully creates or stops a DepthCache, it could update its own local backup copy immediately (add/remove the DC entry)
- On next sync, mgmt overwrites with the authoritative version as usual — this "flattens" the log
- If mgmt crashes and recovers from a DCN, it gets the version that includes locally-applied changes → gap closed

**Variants to consider:**
- Single create: DCN updates local backup after successful create
- Bulk create: DCN updates local backup once after the full batch
- Stop: DCN updates local backup before delete (so the old state is preserved if stop fails)
- Should restapi pods do the same? (they also hold a backup copy)

**Risks:**
- Concurrent creates on multiple DCNs could produce conflicting local states
- Local backup format must stay compatible with mgmt's `replace_data()`
- Need to handle the case where a DCN's local update is based on a stale backup (missed a sync)

**Decision:** Deferred — Oliver wants to visualize the full flow before implementing.

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
