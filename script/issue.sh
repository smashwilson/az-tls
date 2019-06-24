#!/bin/sh

docker build -t quay.io/smashwilson/az-tls:local .
exec docker run \
  --rm \
  --env EMAIL="${EMAIL}" \
  --env AZ_COORDINATOR_ADDR="https://coordinator.azurefire.net:8443" \
  --env AZ_COORDINATOR_TOKEN \
  --env FORCE=yes \
  --env LE_PRODUCTION \
  quay.io/smashwilson/az-tls:local
