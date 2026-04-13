cd ./docs/helm
helm package ../../dev/helm/ubdcc/
helm repo index . --url https://oliver-zehentleitner.github.io/unicorn-depthcache-cluster-for-binance/helm
