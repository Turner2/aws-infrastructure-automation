"""
Configuration module for AWS infrastructure deployment.
Contains all configurable parameters for the deployment.
"""

import os
from typing import Dict, Any

# Template Configuration
TEMPLATE_NAME = "barista-cafe"  # Change this to use different tooplate templates
TEMPLATE_ID = "2137"  # Tooplate template ID for Barista Cafe
TEMPLATE_FILE = "2137_barista_cafe"  # Full template filename without .zip

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# EC2 Configuration
INSTANCE_TYPE = "t2.micro"
AMI_NAME_FILTER = "al2023-ami-2023.*-x86_64"  # Amazon Linux 2023

# Resource Naming
def get_resource_names() -> Dict[str, str]:
    """Generate resource names based on template name."""
    return {
        "key_pair": f"{TEMPLATE_NAME}-keypair",
        "security_group": f"{TEMPLATE_NAME}-sg",
        "instance": f"{TEMPLATE_NAME}-instance",
        "alb": f"{TEMPLATE_NAME}-alb",
        "target_group": f"{TEMPLATE_NAME}-tg",
        "alb_sg": f"{TEMPLATE_NAME}-alb-sg",
    }

# User Data Script Template
USER_DATA_SCRIPT = """#!/bin/bash
# Log all output to a file for debugging
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "Starting user data script..."
date

# Update system
echo "Updating system packages..."
yum update -y

# Install Apache web server
echo "Installing Apache, wget, and unzip..."
yum install -y httpd wget unzip

# Start and enable Apache
echo "Starting Apache..."
systemctl start httpd
systemctl enable httpd

# Download and setup template from tooplate.com
echo "Downloading template from tooplate.com..."
cd /tmp
wget https://www.tooplate.com/zip-templates/{template_file}.zip

echo "Extracting template..."
unzip -o {template_file}.zip

echo "Copying template files to /var/www/html/..."
cp -r {template_file}/* /var/www/html/

# Set proper permissions
echo "Setting permissions..."
chown -R apache:apache /var/www/html
chmod -R 755 /var/www/html

# Create a custom index page with instance metadata
cat > /var/www/html/instance-info.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Instance Information</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }}
        .info-box {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; }}
        .metadata {{ background: #f9f9f9; padding: 10px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
    </style>
</head>
<body>
    <div class="info-box">
        <h1>AWS Deployment Info</h1>
        <div class="metadata">
            <strong>Instance ID:</strong> <span id="instance-id">Loading...</span><br>
            <strong>Availability Zone:</strong> <span id="az">Loading...</span><br>
            <strong>Template:</strong> {template_name}<br>
            <strong>Deployed:</strong> $(date)
        </div>
        <p><a href="/">← Back to main site</a></p>
    </div>
    <script>
        fetch('http://169.254.169.254/latest/meta-data/instance-id')
            .then(r => r.text())
            .then(data => document.getElementById('instance-id').textContent = data);
        fetch('http://169.254.169.254/latest/meta-data/placement/availability-zone')
            .then(r => r.text())
            .then(data => document.getElementById('az').textContent = data);
    </script>
</body>
</html>
EOF

# Restart Apache
echo "Restarting Apache..."
systemctl restart httpd

echo "Setup complete! Website is ready."
echo "User data script finished at $(date)"
"""

def get_user_data() -> str:
    """Get the formatted user data script."""
    return USER_DATA_SCRIPT.format(
        template_id=TEMPLATE_ID,
        template_file=TEMPLATE_FILE,
        template_name=TEMPLATE_NAME
    )

# Security Group Rules
INSTANCE_SG_RULES = [
    {
        "IpProtocol": "tcp",
        "FromPort": 22,
        "ToPort": 22,
        "Description": "SSH access from my IP"
    },
    {
        "IpProtocol": "tcp",
        "FromPort": 80,
        "ToPort": 80,
        "CidrIp": "0.0.0.0/0",
        "Description": "HTTP access from anywhere"
    }
]

ALB_SG_RULES = [
    {
        "IpProtocol": "tcp",
        "FromPort": 80,
        "ToPort": 80,
        "CidrIp": "0.0.0.0/0",
        "Description": "HTTP access from anywhere"
    }
]

# Tags
def get_tags() -> list:
    """Get common tags for all resources."""
    return [
        {"Key": "Project", "Value": TEMPLATE_NAME},
        {"Key": "ManagedBy", "Value": "Boto3-Automation"},
        {"Key": "Environment", "Value": "Demo"}
    ]
