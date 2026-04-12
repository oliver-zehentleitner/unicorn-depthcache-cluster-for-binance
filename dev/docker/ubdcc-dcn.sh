#!/usr/bin/env bash

set -e

VERSION="0.1.4"

echo Deploying UBDCC DepthCacheCluster $VERSION to https://i018oau9.c1.de1.container-registry.ovh.net/harbor/projects/3/repositories

docker build -f container/generic_loader/Dockerfile.ubdcc-dcn -t ubdcc-dcn .
docker login i018oau9.c1.de1.container-registry.ovh.net
docker tag ubdcc-dcn:latest i018oau9.c1.de1.container-registry.ovh.net/library/ubdcc-dcn:$VERSION
docker push i018oau9.c1.de1.container-registry.ovh.net/library/ubdcc-dcn:$VERSION
