#!/usr/bin/env bash
# Package the Helm chart and regenerate the repo index.
# Run from the repo root: bash dev/helm/release.sh
cd ./docs/helm
helm package ../../dev/helm/ubdcc/
helm repo index . --url https://oliver-zehentleitner.github.io/unicorn-binance-depth-cache-cluster/helm
