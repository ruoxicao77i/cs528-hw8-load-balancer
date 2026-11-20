#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STARTUP_PATH="$SCRIPT_DIR/startup.sh"

REGION_ZONES=("us-south1-a" "us-south1-b")
NAMES=("server1" "server2")

for i in 0 1; do
  gcloud compute instances create "${NAMES[$i]}" \
    --zone="${REGION_ZONES[$i]}" \
    --tags=my-lb \
    --machine-type=e2-micro \
    --image-family=debian-12 \
    --image-project=debian-cloud \
    --scopes=cloud-platform \
    --metadata-from-file=startup-script="$STARTUP_PATH"
done

