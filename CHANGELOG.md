# unicorn-depthcache-cluster-for-binance Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to 
[Semantic Versioning](http://semver.org/).

[Discussions about unicorn-depthcache-cluster-for-binance releases!](https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance/discussions/categories/releases)

[How to upgrade to the latest version!](https://oliver-zehentleitner.github.io/unicorn-depthcache-cluster-for-binance/readme.html#installation-and-upgrade)

## 0.2.0
### Added
- AGENTS.md and TASKS.md
### Changed
- Rebranded from LUCIT to open source MIT
- Renamed packages: `lucit-ubdcc-*` → `ubdcc-*`, namespaces: `lucit_ubdcc_*` → `ubdcc_*`
- Kubernetes namespace: `lucit-ubdcc` → `ubdcc`
- LICENSE: LSOSL → MIT
- Author: LUCIT Systems and Development → Oliver Zehentleitner
- All URLs updated from lucit.tech/shop.lucit.services to GitHub
- Sphinx docs theme: `python_docs_theme_lucit` → `alabaster`
### Fixed
- `create_depth_cache()` → `create_depthcache()` in `DepthCacheNode.py` (deprecated method call)
- Per-package LICENSE files replaced with correct MIT license
- Remaining LUCIT references in file headers, pyproject.toml descriptions, and per-package CHANGELOGs
- UBLDC dependency pin: `unicorn_binance_local_depth_cache==2.6.0` → `unicorn-binance-local-depth-cache>=2.8.1`
### Removed
- LUCIT licensing system (LicensingManager, LicensingExceptions, submit_license endpoints)
- `lucit-licensing-python` dependency from all packages
- License params (`lucit_api_secret`, `lucit_license_token`) from UBLDC instantiation in DCN

## 0.1.4
### Fixed
- https://github.com/oliver-zehentleitner/unicorn-depthcache-cluster-for-binance/issues/8 - We don't overwrite 
  the None anymore.

## 0.1.3
MVP release!