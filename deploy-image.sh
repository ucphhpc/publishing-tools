#!/bin/bash
BUILD_ARGS=$1
TAG=$2
EXTRA_TAG=$3

if [[ -n ${DOCKERHUB_USERNAME} ]] && [[ -n ${DOCKERHUB_PASSWORD} ]]; then
    echo "${DOCKERHUB_PASSWORD}" | docker login -u ${DOCKERHUB_USERNAME} --password-stdin
fi

make build TAG=${TAG} ARGS=${BUILD_ARGS}
make push TAG=${TAG} ARGS=${BUILD_ARGS}

# If the EXTRA_TAG is set.
# Link it to the original tag and push that version as well
if [[ -n ${EXTRA_TAG} ]]; then
    make build TAG=${!EXTRA_TAG:0:8} ARGS=${BUILD_ARGS}
    make push TAG=${!EXTRA_TAG:0:8} ARGS=${BUILD_ARGS}
fi