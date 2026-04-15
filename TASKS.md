# TASKS.md — UNICORN Binance DepthCache Cluster

Open development tasks, ideas, and decisions.

---

## In Progress

*(none)*

---

## Backlog

### [ ] Update Helm chart and K8s YAMLs to ghcr.io
- Helm templates still reference old OVH registry `i018oau9.c1.de1.container-registry.ovh.net/library/`
- admin/k8s/*.yaml still have old SHA256 digests from OVH
- Update to `ghcr.io/oliver-zehentleitner/ubdcc-*:<version>`
- Consider: DCN as Deployment (replicas=n) instead of DaemonSet (1 per node) to support 1 DCN per CPU core

### [ ] Docker Compose
- `docker compose up` → full cluster running
- Configurable DCN count via environment variable or compose profiles
- No K8s needed, familiar to most devs

### [ ] Multi-arch Docker images
- Currently amd64 only
- Add arm64 for Apple Silicon / ARM servers
- docker/build-push-action with `platforms: linux/amd64,linux/arm64`

### [ ] Add unit tests
- No test coverage beyond placeholder exists
- Start with mocked unit tests for `Database.py` and `App.py` logic

### [ ] Secure the internal mgmt↔DCN API
- Current state (0.4.0): API credentials live in the cluster DB in cleartext and
  are served to DCNs over plain HTTP on the internal API. Mitigated only by
  network isolation (user's responsibility, documented in README).
- Next layers to consider (from innermost outward):
  - Mutual authentication between pods (shared cluster secret or mTLS)
  - Signed/encrypted credential transport on `/ubdcc_assign_credentials`
  - At-rest encryption for credentials in the DB backup
  - Optional credential storage backend (env var, file, K8s secret, vault)
- Design needs its own round — don't bolt on ad-hoc.

### [ ] Audit and fix all silent except/pass blocks
- Suite-wide initiative — same task tracked in all unicorn-* repos

---

## Ideas — Distribution & Accessibility

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

---

## Ideas — Architecture

### [ ] DCN-local DB updates as distributed transaction log
**Status:** Concept only — needs visualization before implementation.

**Problem:** If mgmt crashes between a `create_depthcache`/`stop_depthcache` and the next node sync, the restored DB is missing that change.

**Concept:**
- Each DCN already holds a local copy of the mgmt DB (`ubdcc_mgmt_backup`)
- When a DCN successfully creates or stops a DepthCache, it could update its own local backup copy immediately
- On next sync, mgmt overwrites with the authoritative version — this "flattens" the log
- If mgmt crashes and recovers from a DCN, it gets the version that includes locally-applied changes

**Variants:** Single create (update after add), bulk create (update once after batch), stop (update before delete). Should restapi also?

**Risks:** Concurrent creates on multiple DCNs → conflicting local states; stale backup → DCN updates based on old state.

**Decision:** Deferred — Oliver wants to visualize the full flow before implementing.

---

## Done (0.3.x cycle)

### [x] CLI cluster manager (`ubdcc` package)
- `ubdcc start --dcn N` with interactive `ubdcc>` console
- Commands: status, add-dcn, remove-dcn (by count or name), restart, stop, help
- `.ubdcc` state file for auto port detection
- `python -m ubdcc` dev entry point

### [x] Docker → ghcr.io migration
- `.github/workflows/docker_build.yml` builds 3 images in parallel
- Pushes to `ghcr.io/oliver-zehentleitner/ubdcc-{dcn,mgmt,restapi}:<version>+latest`
- Dropped `-latest` variants and `dev_station` container
- Base image: python:3.14-slim

### [x] Python 3.9-3.14 support on Linux/macOS/Windows
- All 5 packages, UBWA build pattern (cibuildwheel v3.4.1, 3 OS matrix)

### [x] Separate GitHub Release from PyPI workflows
- `gh_release.yml` handles release creation once per tag
- Individual build workflows only push to PyPI

### [x] REST API improvements
- `/create_depthcaches` supports GET + POST (GET with comma-separated markets for browser debugging)
- `/shutdown` endpoint (dev-mode only) for graceful process shutdown
- `debug=true` includes `post_body` for POST requests
- `mgmt_port` parameter threaded through all services
- SO_REUSEADDR fix for TIME_WAIT after restart
- Port retry on bind failure (race condition fix)
- `os._exit(0)` after /shutdown response (prevents hanging)

### [x] Sphinx docs rebuild
- Restored `python_docs_theme_lucit` (consistent with rest of UBS)
- Added sphinxcontrib-mermaid + myst_fence_as_directive
- create_docs.sh: CNAME fix (> instead of >>), license.rst with title
- 0 build warnings

### [x] README overhaul
- "What is UBDCC?" + "Why?" sections for new users
- Architecture diagram (Mermaid, inline — no Lucidchart dependency)
- Local Setup with CLI as primary path
- Full REST API reference (public + internal endpoints)
- Debug guide, ports table, sizing recommendations

### [x] LUCIT removal + MIT rebrand (0.2.0)
- Package renames: `lucit-ubdcc-*` → `ubdcc-*`
- LICENSE: LSOSL → MIT
- All URLs, headers, project_urls aligned with UBS standard
