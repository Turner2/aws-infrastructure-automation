# Example Configuration Templates

## Available Tooplate Templates

Here are some popular templates you can use by updating `config.py`:

### 1. Barista Cafe (Default)
```python
TEMPLATE_NAME = "barista-cafe"
TEMPLATE_ID = "2137"
```
![Barista Cafe](https://www.tooplate.com/screenshots/2137_barista_cafe.jpg)

### 2. Crispy Kitchen
```python
TEMPLATE_NAME = "crispy-kitchen"
TEMPLATE_ID = "2129"
```

### 3. The Corp
```python
TEMPLATE_NAME = "the-corp"
TEMPLATE_ID = "2120"
```

### 4. Mini Profile
```python
TEMPLATE_NAME = "mini-profile"
TEMPLATE_ID = "2119"
```

### 5. Snapshot
```python
TEMPLATE_NAME = "snapshot"
TEMPLATE_ID = "2113"
```

## Configuration Examples

### Development Environment
```python
# config.py for Development
TEMPLATE_NAME = "dev-barista"
AWS_REGION = "us-east-1"
INSTANCE_TYPE = "t2.micro"

def get_tags() -> list:
    return [
        {"Key": "Project", "Value": TEMPLATE_NAME},
        {"Key": "Environment", "Value": "Development"},
        {"Key": "AutoShutdown", "Value": "True"}
    ]
```

### Production Environment
```python
# config.py for Production
TEMPLATE_NAME = "prod-barista"
AWS_REGION = "us-west-2"
INSTANCE_TYPE = "t2.small"

def get_tags() -> list:
    return [
        {"Key": "Project", "Value": TEMPLATE_NAME},
        {"Key": "Environment", "Value": "Production"},
        {"Key": "Backup", "Value": "Required"},
        {"Key": "CostCenter", "Value": "Engineering"}
    ]
```

### Multi-Region Setup
```python
# Deploy to multiple regions
REGIONS = ["us-east-1", "eu-west-1", "ap-southeast-1"]

for region in REGIONS:
    deployer = InfrastructureDeployer(region=region)
    deployer.deploy()
```

### Custom User Data
```python
# Install additional software
USER_DATA_SCRIPT = """#!/bin/bash
# Update system
yum update -y

# Install Apache, PHP, MySQL
yum install -y httpd php php-mysqlnd mysql

# Install additional tools
yum install -y git wget curl

# Start services
systemctl start httpd
systemctl enable httpd

# Download template
cd /tmp
wget https://www.tooplate.com/zip-templates/{template_id}.zip
unzip -o {template_id}.zip
cp -r {template_id}/* /var/www/html/

# Custom application setup
cd /var/www/html
# Add your custom commands here

# Set permissions
chown -R apache:apache /var/www/html
chmod -R 755 /var/www/html
"""
```

### Custom Security Group Rules
```python
# Add HTTPS support
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
        "Description": "HTTP access"
    },
    {
        "IpProtocol": "tcp",
        "FromPort": 443,
        "ToPort": 443,
        "CidrIp": "0.0.0.0/0",
        "Description": "HTTPS access"
    }
]
```

### Different Instance Types
```python
# Free tier
INSTANCE_TYPE = "t2.micro"  # 1 vCPU, 1 GB RAM

# Better performance
INSTANCE_TYPE = "t2.small"  # 1 vCPU, 2 GB RAM
INSTANCE_TYPE = "t2.medium" # 2 vCPU, 4 GB RAM

# Compute optimized
INSTANCE_TYPE = "c5.large"  # 2 vCPU, 4 GB RAM

# Memory optimized
INSTANCE_TYPE = "r5.large"  # 2 vCPU, 16 GB RAM
```

### Different AMI Filters
```python
# Amazon Linux 2023 (default)
AMI_NAME_FILTER = "al2023-ami-2023.*-x86_64"

# Amazon Linux 2
AMI_NAME_FILTER = "amzn2-ami-hvm-*-x86_64-gp2"

# Ubuntu 22.04
AMI_NAME_FILTER = "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"

# Ubuntu 20.04
AMI_NAME_FILTER = "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"
```

Note: When using non-Amazon Linux AMIs, update the user data script accordingly:
- Amazon Linux uses `yum`
- Ubuntu uses `apt-get`

## Environment-Specific Deployment

### Using Environment Variables
```python
import os

# config.py
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
INSTANCE_TYPE = os.getenv("INSTANCE_TYPE", "t2.micro")
TEMPLATE_NAME = os.getenv("TEMPLATE_NAME", "barista-cafe")
```

Then deploy with:
```bash
export AWS_REGION=eu-west-1
export INSTANCE_TYPE=t2.small
export TEMPLATE_NAME=my-cafe
python deploy.py
```

## Cost Estimation

### t2.micro (Free Tier Eligible)
- Instance: $0.0116/hour (~$8.50/month)
- ALB: $0.0225/hour (~$16/month)
- Data transfer: First 1 GB free, then $0.09/GB
- **Total: ~$25/month** (with minimal traffic)

### t2.small
- Instance: $0.023/hour (~$17/month)
- ALB: $0.0225/hour (~$16/month)
- **Total: ~$33/month**

*Note: Prices are approximate and vary by region*
