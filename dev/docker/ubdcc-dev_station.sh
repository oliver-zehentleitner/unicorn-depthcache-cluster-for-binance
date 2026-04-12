#!/usr/bin/env bash

set -e

VERSION="0.1.1"

echo Deploying UBDCC Dev Station $VERSION to https://i018oau9.c1.de1.container-registry.ovh.net/harbor/projects/3/repositories

docker build -f container/dev_station/Dockerfile -t ubdcc-dev_station .
docker login i018oau9.c1.de1.container-registry.ovh.net
docker tag ubdcc-dev_station:latest i018oau9.c1.de1.container-registry.ovh.net/library/ubdcc-dev_station:$VERSION
docker push i018oau9.c1.de1.container-registry.ovh.net/library/ubdcc-dev_station:$VERSION
