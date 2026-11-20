#!/bin/bash
set -euo pipefail

REGION="us-south1"

gcloud compute firewall-rules create hw8-hc-firewall \
    --target-tags my-lb --allow tcp:8000

gcloud compute addresses create network-lb-ip --region $REGION
gcloud compute http-health-checks create hw8-hc \
    --port=8000 \
    --request-path=/health \
    --check-interval=2s \
    --timeout=2s \
    --unhealthy-threshold=2 \
    --healthy-threshold=2
gcloud compute target-pools create www-pool \
    --region $REGION --http-health-check hw8-hc
gcloud compute target-pools add-instances www-pool \
    --instances server1 --instances-zone=us-south1-a
gcloud compute target-pools add-instances www-pool \
    --instances server2 --instances-zone=us-south1-b
gcloud compute forwarding-rules create hw8-rule \
    --region  $REGION \
    --ports 8000 \
    --address network-lb-ip \
    --target-pool www-pool



