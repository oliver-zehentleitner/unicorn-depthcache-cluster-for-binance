#!/usr/bin/env bash

set -e

VERSION="0.1.4-latest"

echo Deploying UBDCC Mgmt $VERSION to https://i018oau9.c1.de1.container-registry.ovh.net/harbor/projects/3/repositories

docker build -f container/generic_loader/Dockerfile.ubdcc-mgmt-latest -t ubdcc-mgmt .
docker login i018oau9.c1.de1.container-registry.ovh.net
docker tag ubdcc-mgmt:latest i018oau9.c1.de1.container-registry.ovh.net/library/ubdcc-mgmt:$VERSION
docker push i018oau9.c1.de1.container-registry.ovh.net/library/ubdcc-mgmt:$VERSION
