#!/bin/bash -e

if ! docker network inspect supra-projector >/dev/null 2>&1; then
    docker network create supra-projector
fi

docker run --name vnc-rbi -d \
    --network supra-projector \
	-p 5900:5900 \
	-e SUPRA_PROJECTOR_NETWORK='supra-projector' \
	-e SUPRA_PROJECTOR_IMAGE='projector-chrome' \
    -e LOG_LEVEL='debug' \
	-v /var/run/docker.sock:/var/run/docker.sock \
	supraaxes/suprarbi-vnc
