#!/bin/bash
set -euxo pipefail

APP_DIR=/opt/app
BUCKET=cs528-ruoxi-pagerank
mkdir -p "$APP_DIR"

apt-get update
apt-get install -y python3-venv
if [ ! -d "$APP_DIR/venv" ]; then
  python3 -m venv "$APP_DIR/venv"
fi
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install \
  google-cloud-storage \
  google-cloud-logging \
  google-cloud-pubsub

gcloud storage cp "gs://$BUCKET/code/server.py" "$APP_DIR/server.py"

cat > /etc/systemd/system/webserver.service <<EOF
[Unit]
Description=HW8 web server
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/server.py
WorkingDirectory=$APP_DIR
Environment=PYTHONUNBUFFERED=1
Restart=no

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable webserver
systemctl restart webserver