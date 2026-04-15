# AGENTS.md — UNICORN Binance DepthCache Cluster

## Planning & Backlog

Open development tasks and decisions are tracked in **[TASKS.md](TASKS.md)**.

---

## Project Overview

Distributed microservice cluster (MIT License) that manages multiple local Binance order book depth caches. Runs on Kubernetes OR locally via `pip install ubdcc`. Clients interact via a public REST API — no local Binance connection required on the client side.

**Abbreviation:** UBDCC
**Current Version:** 0.4.0.dev
**Author:** Oliver Zehentleitner
**Python:** 3.9-3.14 on Linux, macOS, Windows
**Runtime:** Kubernetes, Docker, or local processes

---

## Package Structure

Five interdependent Python packages under `packages/`:

| Package (PyPI) | Directory | Namespace | Purpose |
|---|---|---|---|
| `ubdcc-shared-modules` | `packages/ubdcc-shared-modules/` | `ubdcc_shared_modules` | Core library: App, Database, REST base, server |
| `ubdcc-mgmt` | `packages/ubdcc-mgmt/` | `ubdcc_mgmt` | Management service: orchestration, node registry, DC distribution |
| `ubdcc-dcn` | `packages/ubdcc-dcn/` | `ubdcc_dcn` | Depth Cache Node: runs UBLDC instances per pod |
| `ubdcc-restapi` | `packages/ubdcc-restapi/` | `ubdcc_restapi` | Public REST API: proxies requests to DCN pods |
| `ubdcc` | `packages/ubdcc/` | `ubdcc` | Meta-package + CLI cluster manager |

**Dependency order:** shared-modules ← mgmt, dcn, restapi ← ubdcc (meta)

The 4 core packages are Cython-compiled. `ubdcc` is pure Python.

---

## Architecture

```
Client (HTTP, any language)
  ↓
ubdcc-restapi  (LoadBalancer, port 80 in K8s / 42081 local)
  ↓ proxies to mgmt for routing info
ubdcc-mgmt     (internal, port 8080 in K8s / 42080 local)
  ├── distributes depth caches to DCN pods
  ├── manages in-memory Database (depthcaches, pods, nodes)
  └── DB replicated to every node via /ubdcc_mgmt_backup (self-healing)

ubdcc-dcn      (multiple, port 8080 in K8s / 42082+ local)
  ├── registers with mgmt on startup
  ├── runs BinanceLocalDepthCacheManager (UBLDC) per DepthCache
  └── reports status to mgmt, holds DB backup
```

**Dev mode:** When K8s config is not available, services run locally with default ports 42080 (mgmt), 42081 (restapi), 42082+ (DCN, auto-increment).

**Recommended sizing:** One DCN per CPU core (GIL limits each process to one core).

---

## Key Files

| File | Purpose |
|---|---|
| `ubdcc_shared_modules/App.py` | Base app class: runtime info, REST server, node registration/sync, shutdown |
| `ubdcc_shared_modules/Database.py` | Thread-safe in-memory store: depthcaches, pods, nodes |
| `ubdcc_shared_modules/RestEndpointsBase.py` | Shared REST helpers: test, shutdown, backup sync, response formatting |
| `ubdcc_shared_modules/ServiceBase.py` | Base class for all three services, port retry on bind failure |
| `ubdcc_mgmt/RestEndpoints.py` | All cluster management endpoints |
| `ubdcc_dcn/DepthCacheNode.py` | Main DCN loop: creates/stops UBLDC instances based on mgmt assignments |
| `ubdcc_restapi/RestEndpoints.py` | Public API: proxies get_asks, get_bids, create_depthcache(s), etc. |
| `ubdcc/cli.py` | CLI cluster manager with interactive `ubdcc>` console |

---

## Public REST API Endpoints (via restapi)

| Endpoint | Method | Description |
|---|---|---|
| `/test` | GET | Health check |
| `/create_depthcache` | GET | Create a single DepthCache |
| `/create_depthcaches` | GET/POST | Create multiple (POST: JSON body; GET: comma-separated markets) |
| `/get_asks` / `/get_bids` | GET | Get order book side (limit_count, threshold_volume) |
| `/get_cluster_info` | GET | Cluster state: pods, nodes, depthcaches |
| `/get_depthcache_list` | GET | List all DepthCaches with status |
| `/get_depthcache_info` | GET | Info for a specific DepthCache |
| `/stop_depthcache` | GET | Stop and remove a DepthCache |
| `/shutdown` | GET | **Dev mode only** — shut down this process |

All accept `debug=true` for timing/routing details.

---

## CLI (ubdcc package)

```bash
pip install ubdcc
ubdcc start --dcn 4          # starts mgmt + restapi + 4 DCN in interactive shell
```

Interactive shell commands: `status`, `add-dcn [count]`, `remove-dcn <count|name>`, `restart <name>`, `stop`, `help`.

`.ubdcc` state file in CWD stores the mgmt port so `status`/`stop` find it without `--port`.

---

## Kubernetes Resources

- **Namespace:** `ubdcc`
- **Manifests:** `admin/k8s/` (StatefulSets, DaemonSet for DCN, Services)
- **Setup:** `admin/k8s/setup/` (namespace, RBAC)
- **Helm chart:** `dev/helm/ubdcc/`

**Note:** Helm chart and K8s YAMLs still reference the old OVH registry — migration to ghcr.io pending (see TASKS.md).

---

## Docker

- **Dockerfiles:** `container/generic_loader/Dockerfile.ubdcc-{dcn,mgmt,restapi}`
- **Base image:** `python:3.14-slim`
- **Registry:** `ghcr.io/oliver-zehentleitner/ubdcc-{dcn,mgmt,restapi}:<version>`
- **Build:** `.github/workflows/docker_build.yml` — `workflow_dispatch` with version input, pushes to ghcr.io via `GITHUB_TOKEN`

---

## Version Management

- `dev/set_version.py <new_version>` — updates the version across all listed files
- Config: `dev/set_version_config.yml`
- Current version: `0.4.0.dev`

---

## Build & Release Flow

1. `python dev/set_version.py X.Y.Z` — bumps version in all files
2. Commit, push, tag
3. Trigger 5 PyPI build workflows (one per package) — wheels land on PyPI
4. Trigger `gh_release.yml` — creates the GitHub release
5. Trigger `docker_build.yml` with version input — images land on ghcr.io

CI workflows in `.github/workflows/`:
- `build_wheels_ubdcc_{dcn,mgmt,restapi,shared_modules}.yml` — Cython builds (3 OS matrix, cp39-cp314)
- `build_wheels_ubdcc.yml` — pure Python wheel + sdist
- `docker_build.yml` — Docker images to ghcr.io
- `gh_release.yml` — GitHub Release creation
- `unit-tests.yml` — Python 3.9 + 3.14 pytest with Codecov
- `codeql.yml` — static analysis

---

## Tests

Placeholder tests only — see TASKS.md.

---

## Notes & Gotchas

- `test_connection()` in UBLDC's `cluster.py` checks for `app.name == "ubdcc-restapi"` — matches the app_name in `RestApi.py`
- Dev mode activates when K8s config is not loadable
- `Database.revise()` runs periodically via mgmt — updates nodes, removes old pods, manages DC distribution
- Self-healing state: DB is replicated to every node; on mgmt restart, mgmt recovers from the node with the most recent backup timestamp
- Port retry fallback: if the REST server can't bind on the first attempt (race condition), it increments and tries again
- `SO_REUSEADDR` is set on the port check to handle TIME_WAIT after a restart
- `os._exit(0)` is scheduled 0.5s after the `/shutdown` response to ensure the process terminates even if the main loop is stuck in `asyncio.sleep`
