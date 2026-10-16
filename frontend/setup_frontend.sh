#!/bin/bash
set -euo pipefail

# Usage from the frontend directory on the FRONTEND EC2 instance:
# ./setup_frontend.sh <BACKEND_PUBLIC_IPV4>
if [ "$#" -ne 1 ]; then
  echo "Usage: ./setup_frontend.sh <BACKEND_PUBLIC_IPV4>"
  exit 1
fi
BACKEND_IP="$1"
APP_DIR="/var/www/html"

sudo dnf update -y
sudo dnf install -y httpd
sudo systemctl enable --now httpd
sudo mkdir -p "$APP_DIR"
sudo cp index.html style.css script.js config.js "$APP_DIR/"

# Point the existing frontend at the backend EC2 public IPv4 address.
sudo sed -i "s|http://BACKEND_PUBLIC_IP:8000|http://${BACKEND_IP}:8000|g" "$APP_DIR/config.js"
sudo chown -R apache:apache "$APP_DIR"
sudo systemctl restart httpd

echo "Frontend deployed. Check http://$(curl -s https://checkip.amazonaws.com)/"
echo "Configured backend API: http://${BACKEND_IP}:8000"
