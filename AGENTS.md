# AGENTS.md — UNICORN DepthCache Cluster for Binance

## Planning & Backlog

Open development tasks and decisions are tracked in **[TASKS.md](TASKS.md)**.

---

## Project Overview

Kubernetes-based microservice cluster (MIT License) that manages multiple local Binance order book depth caches across cluster nodes. Clients interact via a public REST API; no local Binance connection required on the client side.

**Abbreviation:** UBDCC  
**Current Version:** 0.2.0  
**Author:** Oliver Zehentleitner  
**Python:** 3.12+  
**Runtime:** Kubernetes (also runnable in dev mode without K8s)

---

## Package Structure

Four interdependent Python packages under `packages/`:

| Package (PyPI) | Directory | Namespace | Purpose |
|---|---|---|---|
| `ubdcc-shared-modules` | `packages/ubdcc-shared-modules/` | `ubdcc_shared_modules` | Core library: App, Database, REST base, server |
| `ubdcc-mgmt` | `packages/ubdcc-mgmt/` | `ubdcc_mgmt` | Management service: orchestration, node registry, DC distribution |
| `ubdcc-dcn` | `packages/ubdcc-dcn/` | `ubdcc_dcn` | Depth Cache Node: runs UBLDC instances per pod |
| `ubdcc-restapi` | `packages/ubdcc-restapi/` | `ubdcc_restapi` | Public REST API: proxies requests to DCN pods |

**Dependency order:** shared-modules ← mgmt, dcn, restapi

---

## Architecture

```
Client (HTTP)
  ↓
ubdcc-restapi  (LoadBalancer, port 80)
  ↓ proxies to mgmt for addresses
ubdcc-mgmt     (ClusterIP, port 4280 / 8080)
  ├── watches K8s nodes/pods
  ├── distributes depth caches to DCN pods
  └── manages in-memory Database (depthcaches, pods, nodes)

ubdcc-dcn      (one pod per node, port 8080)
  ├── registered with mgmt on startup
  ├── runs BinanceLocalDepthCacheManager (UBLDC) per exchange/update_interval
  └── reports depth cache status back to mgmt
```

**Dev mode:** When K8s config is not available, all three services run locally with different ports (42080/42081/42082).

---

## Key Files

| File | Purpose |
|---|---|
| `ubdcc_shared_modules/App.py` | Base app class: K8s runtime info, REST server, node registration/sync, shutdown |
| `ubdcc_shared_modules/Database.py` | Thread-safe in-memory store: depthcaches, pods, nodes |
| `ubdcc_shared_modules/RestEndpointsBase.py` | Shared REST helpers: test endpoint, backup sync, response formatting |
| `ubdcc_shared_modules/ServiceBase.py` | Base class for all three services |
| `ubdcc_mgmt/RestEndpoints.py` | All cluster management endpoints |
| `ubdcc_dcn/DepthCacheNode.py` | Main DCN loop: creates/stops UBLDC instances based on mgmt assignments |
| `ubdcc_restapi/RestEndpoints.py` | Public API: proxies get_asks, get_bids, create_depthcache etc. |

---

## REST API Endpoints

Defined in each service's `RestEndpoints.py`. Public endpoints (via restapi):

| Endpoint | Method | Description |
|---|---|---|
| `/test` | GET | Health check — returns `{"app": {"name": "ubdcc-restapi"}, "result": "OK"}` |
| `/create_depthcache` | GET | Create a depth cache for a market |
| `/create_depthcaches` | GET | Create multiple depth caches (base64-encoded market list) |
| `/get_asks` | GET | Get ask orders for a market |
| `/get_bids` | GET | Get bid orders for a market |
| `/get_cluster_info` | GET | Cluster status: nodes, pods, depthcaches |
| `/get_depthcache_list` | GET | List all active depth caches |
| `/get_depthcache_info` | GET | Info for a specific depth cache |
| `/stop_depthcache` | GET | Stop a depth cache |

---

## Kubernetes Resources

- **Namespace:** `ubdcc`
- **Manifests:** `admin/k8s/` (StatefulSets, Deployments, Services)
- **Setup:** `admin/k8s/setup/` (namespace, RBAC)
- **Helm chart:** `dev/helm/ubdcc/`

---

## Docker

- **Dockerfiles:** `container/generic_loader/Dockerfile.ubdcc-{dcn,mgmt,restapi}[-latest]`
- **Requirements:** `container/generic_loader/requirements-ubdcc_{dcn,mgmt,restapi}[-latest].txt`
- **Build scripts:** `dev/docker/ubdcc-{dcn,mgmt,restapi}[-latest].sh`
- **Dev station:** `container/dev_station/` — all services in one container for local testing
- **Registry:** TBD (migrating from OVH private registry)

---

## Dependencies

- `ubdcc-shared-modules` deps: `aiohttp`, `Cython`, `fastapi`, `kubernetes`, `uvicorn`
- `ubdcc-dcn` additional: `unicorn-binance-local-depth-cache>=2.8.1`
- All packages: Python 3.12+

---

## Version Management

- `dev/set_version.py` + `dev/set_version_config.yml` — update version across all packages
- Version currently in sync across all `setup.py` and `pyproject.toml` files
- Current version: `0.2.0`

---

## Build & Release

```bash
# Build wheel for a package (example: shared-modules)
cd packages/ubdcc-shared-modules
python setup.py bdist_wheel
```

CI/CD: `.github/workflows/build_wheels_ubdcc_{dcn,mgmt,restapi,shared_modules}.yml`  
Triggered manually via `workflow_dispatch`. Builds Linux wheels + publishes to PyPI.

---

## Tests

No automated tests exist yet — see TASKS.md.

---

## Notes & Gotchas

- `test_connection()` in UBLDC's `cluster.py` checks for `app.name == "ubdcc-restapi"` — this matches the app_name set in `RestApi.py`
- Dev mode activates automatically when K8s config is not loadable
- `Database.revise()` runs periodically via mgmt — updates nodes, removes old pods, manages DC distribution
- Docs need full Sphinx rebuild after the LUCIT→MIT migration (theme changed to `alabaster`)
