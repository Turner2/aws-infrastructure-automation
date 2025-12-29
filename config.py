"""
Configuration module for AWS infrastructure deployment.
Contains all configurable parameters for the deployment.
"""

import os
from typing import Dict, Any

# Template Configuration
TEMPLATE_NAME = "barista-cafe"  # Change this to use different tooplate templates
TEMPLATE_ID = "2137"  # Tooplate template ID for Barista Cafe

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
# Update system
yum update -y

# Install Apache web server
yum install -y httpd wget unzip

# Start and enable Apache
systemctl start httpd
systemctl enable httpd

# Download and setup template from tooplate.com
cd /tmp
wget https://www.tooplate.com/zip-templates/{template_id}.zip
unzip -o {template_id}.zip
cp -r {template_id}/* /var/www/html/

# Set proper permissions
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
        <h1>🚀 AWS Deployment Info</h1>
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
systemctl restart httpd

echo "Setup complete! Website is ready."
"""

def get_user_data() -> str:
    """Get the formatted user data script."""
    return USER_DATA_SCRIPT.format(
        template_id=TEMPLATE_ID,
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
