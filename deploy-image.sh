#!/bin/bash
BUILD_ARGS=$1
TAG=$2
COMMIT_TAG=$3
EXTRA_TAG=$4

if [[ -n ${DOCKERHUB_USERNAME} ]] && [[ -n ${DOCKERHUB_PASSWORD} ]]; then
    echo "${DOCKERHUB_PASSWORD}" | docker login -u ${DOCKERHUB_USERNAME} --password-stdin
fi

# Prepare for a clean build
make clean
# Build from scratch and push
make TAG=${TAG} ARGS=${BUILD_ARGS}
make dockerpush TAG=${TAG} ARGS=${BUILD_ARGS}

# If the COMMIT_TAG is set.
# Link it to the original tag and push that version as well
if [[ -n ${COMMIT_TAG} ]]; then
    make TAG=${!COMMIT_TAG:0:8} ARGS=${BUILD_ARGS}
    make dockerpush TAG=${!COMMIT_TAG:0:8} ARGS=${BUILD_ARGS}
fi

# If the EXTRA_TAG is set.
# Link it to the original tag and push that version as well
if [[ -n ${EXTRA_TAG} ]]; then
    make TAG=${EXTRA_TAG} ARGS=${BUILD_ARGS}
    make dockerpush TAG=${EXTRA_TAG} ARGS=${BUILD_ARGS}
fi