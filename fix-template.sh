#!/bin/bash

# Script to fix the template on the existing EC2 instance
# This will download and install the correct Barista Cafe template

INSTANCE_IP="3.236.120.78"
KEY_FILE="barista-cafe-keypair.pem"

echo "================================================"
echo "Fixing Template on EC2 Instance"
echo "================================================"
echo ""
echo "Instance IP: $INSTANCE_IP"
echo "Connecting and fixing template..."
echo ""

# SSH into instance and run commands to fix the template
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ec2-user@$INSTANCE_IP << 'ENDSSH'
set -e

echo "Downloading correct template from tooplate.com..."
cd /tmp
sudo rm -f 2137_barista_cafe.zip
sudo rm -rf 2137_barista_cafe
wget https://www.tooplate.com/zip-templates/2137_barista_cafe.zip

echo "Extracting template..."
unzip -o 2137_barista_cafe.zip

echo "Backing up current web files..."
sudo mkdir -p /var/www/html.backup
sudo cp -r /var/www/html/* /var/www/html.backup/ 2>/dev/null || true

echo "Installing template to /var/www/html/..."
sudo cp -r 2137_barista_cafe/* /var/www/html/

echo "Setting permissions..."
sudo chown -R apache:apache /var/www/html
sudo chmod -R 755 /var/www/html

echo "Restarting Apache..."
sudo systemctl restart httpd

echo ""
echo "Template installation complete!"
echo ""
echo "Files in /var/www/html/:"
ls -lh /var/www/html/ | head -10

ENDSSH

echo ""
echo "================================================"
echo "Template Fixed Successfully!"
echo "================================================"
echo ""
echo "Visit your website:"
echo "   http://$INSTANCE_IP"
echo ""
echo "The website should now show the Barista Cafe template!"
echo "================================================"
