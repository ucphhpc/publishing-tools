#!/bin/bash
NOTEBOOK=$1
BUILD_ARGS=$2
TAG=$3
COMMIT_TAG=$4
EXTRA_TAG=$5
>
if [[ -n ${DOCKERHUB_USERNAME} ]] && [[ -n ${DOCKERHUB_PASSWORD} ]]; then
    echo "${DOCKERHUB_PASSWORD}" | docker login -u ${DOCKERHUB_USERNAME} --password-stdin
fi

# Prepare for a clean build
make clean
# Build from scratch and push
make build/${NOTEBOOK} TAG=${TAG} ARGS=${BUILD_ARGS}
make push/${NOTEBOOK} TAG=${TAG} ARGS=${BUILD_ARGS}

# If the COMMIT_TAG is set.
# Link it to the original tag and push that version as well
if [[ -n ${COMMIT_TAG} ]]; then
    ln -s Dockerfile.${TAG} ${NOTEBOOK}/Dockerfile.${!COMMIT_TAG:0:8}

    make TAG=${!COMMIT_TAG:0:8} ARGS=${BUILD_ARGS}
    make dockerpush TAG=${!COMMIT_TAG:0:8} ARGS=${BUILD_ARGS}
fi

# If the EXTRA_TAG is set.
# Link it to the original tag and push that version as well
if [[ -n ${EXTRA_TAG} ]]; then
    ln -s Dockerfile.${TAG} ${NOTEBOOK}/Dockerfile.${EXTRA_TAG}

    make build/${NOTEBOOK} TAG=${EXTRA_TAG} ARGS=${BUILD_ARGS}
    make push/${NOTEBOOK} TAG=${EXTRA_TAG} ARGS=${BUILD_ARGS}
fi