# CS528 Homework 8

## Setup

1. Create 2 instances running the web server

The two instances are in different zones and the same region.

```shell
gcloud compute instances create server1 \
    --zone=us-central1-a    \
    --tags=hw8-lb   \
    --machine-type=e2-micro \
    --image-family=debian-12    \
    --image-project=debian-cloud    \
    --meta-data=
```

The other machine is set the same way except the zone(can be set to `us-central1-b` or else).

2. Create the firewall rules

```shell
gcloud compute firewall-rules create www-firewall-network-lb \
    --target-tags hw8-lb --allow tcp:80
```