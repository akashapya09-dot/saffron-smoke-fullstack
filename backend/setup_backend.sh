#!/bin/bash
set -euo pipefail

# Run this from the backend directory on the BACKEND EC2 instance.
APP_DIR="/opt/saffron-smoke-backend"
sudo dnf update -y
sudo dnf install -y python3 python3-pip

sudo mkdir -p "$APP_DIR"
sudo cp app.py "$APP_DIR/app.py"
sudo chown -R ec2-user:ec2-user "$APP_DIR"

python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r requirements.txt

sudo tee /etc/systemd/system/saffron-smoke-backend.service >/dev/null <<'SERVICE'
[Unit]
Description=Saffron and Smoke Demo API
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/opt/saffron-smoke-backend
ExecStart=/opt/saffron-smoke-backend/venv/bin/python /opt/saffron-smoke-backend/app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable --now saffron-smoke-backend
sudo systemctl --no-pager --full status saffron-smoke-backend
echo "Backend service installed. Test with: curl http://localhost:8000/api/health"
