# AWS Boto3 Infrastructure Automation - Technical Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Module Documentation](#module-documentation)
4. [API Reference](#api-reference)
5. [Configuration Guide](#configuration-guide)
6. [Deployment Flow](#deployment-flow)
7. [Error Handling](#error-handling)
8. [Security Considerations](#security-considerations)

## Overview

This project provides a production-ready framework for automating AWS infrastructure deployment using Python and Boto3. It follows software engineering best practices including:

- **Separation of Concerns**: Each AWS service is managed by a dedicated module
- **Single Responsibility Principle**: Each class/function has one clear purpose
- **DRY (Don't Repeat Yourself)**: Common functionality is abstracted into utilities
- **Error Handling**: Comprehensive exception handling at every layer
- **Logging**: Structured logging for debugging and monitoring
- **Type Safety**: Python type hints for better code quality

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        deploy.py                             │
│              (Orchestration & Main Entry Point)              │
└──────────┬────────────────────────────────────┬─────────────┘
           │                                    │
           ▼                                    ▼
    ┌─────────────┐                      ┌─────────────┐
    │  config.py  │                      │   utils/    │
    │             │                      │  helpers.py │
    └─────────────┘                      └─────────────┘
           │
           ▼
    ┌─────────────────────────────────────────────────────┐
    │                   modules/                           │
    ├──────────────┬──────────────┬───────────┬──────────┤
    │ keypair.py   │security_group│ec2_instance│ alb.py   │
    │              │    .py       │   .py      │          │
    └──────────────┴──────────────┴───────────┴──────────┘
           │                │              │           │
           └────────────────┴──────────────┴───────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   Boto3      │
                    │  AWS SDK     │
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │     AWS      │
                    │   Services   │
                    └──────────────┘
```

### Data Flow

```
User Executes deploy.py
         │
         ▼
InfrastructureDeployer.__init__()
    • Initialize Boto3 clients
    • Load configuration
    • Create service managers
         │
         ▼
InfrastructureDeployer.deploy()
         │
         ├─► Step 1: Create Key Pair
         │   └─► KeyPairManager.create_key_pair()
         │       └─► EC2 API: create_key_pair()
         │
         ├─► Step 2: Get Public IP
         │   └─► get_my_public_ip()
         │       └─► HTTP: https://checkip.amazonaws.com
         │
         ├─► Step 3: Create Security Groups
         │   ├─► SecurityGroupManager.create_security_group()
         │   │   └─► EC2 API: create_security_group()
         │   └─► SecurityGroupManager.add_ingress_rules()
         │       └─► EC2 API: authorize_security_group_ingress()
         │
         ├─► Step 4: Create EC2 Instance
         │   ├─► EC2InstanceManager.get_ami_id()
         │   │   └─► EC2 API: describe_images()
         │   └─► EC2InstanceManager.create_instance()
         │       ├─► EC2 API: run_instances()
         │       └─► Waiter: instance_running
         │
         └─► Step 5: Create ALB Infrastructure
             ├─► ALBManager.get_all_subnets()
             │   └─► EC2 API: describe_subnets()
             ├─► ALBManager.create_target_group()
             │   └─► ELBv2 API: create_target_group()
             ├─► ALBManager.register_targets()
             │   └─► ELBv2 API: register_targets()
             ├─► ALBManager.create_load_balancer()
             │   ├─► ELBv2 API: create_load_balancer()
             │   └─► Waiter: load_balancer_available
             └─► ALBManager.create_listener()
                 └─► ELBv2 API: create_listener()
```

## Module Documentation

### config.py

**Purpose**: Centralized configuration management

**Key Components**:
- `TEMPLATE_NAME`: Website template name (used for resource naming)
- `TEMPLATE_ID`: Tooplate.com template ID
- `AWS_REGION`: Target AWS region
- `INSTANCE_TYPE`: EC2 instance type
- `AMI_NAME_FILTER`: Amazon Machine Image filter pattern
- `USER_DATA_SCRIPT`: Bash script for instance initialization
- `INSTANCE_SG_RULES`: Security group ingress rules for EC2
- `ALB_SG_RULES`: Security group ingress rules for ALB

**Functions**:
```python
get_resource_names() -> Dict[str, str]
    Returns dictionary of resource names based on template name

get_user_data() -> str
    Returns formatted user data script with template variables

get_tags() -> list
    Returns common tags for all resources
```

### modules/keypair.py

**Class**: `KeyPairManager`

**Purpose**: Manages EC2 key pairs for SSH access

**Methods**:

```python
__init__(ec2_client)
    Initialize with boto3 EC2 client

create_key_pair(key_name: str, save_path: Optional[str] = None) -> Dict[str, Any]
    Create new key pair or return existing one
    Args:
        key_name: Name for the key pair
        save_path: Optional path to save private key
    Returns:
        Dictionary with KeyPairId, KeyName, and Exists flag
    Raises:
        ClientError: If creation fails

delete_key_pair(key_name: str) -> bool
    Delete an existing key pair
    
key_pair_exists(key_name: str) -> bool
    Check if a key pair exists
```

**Example Usage**:
```python
from modules import KeyPairManager
import boto3

ec2_client = boto3.client('ec2', region_name='us-east-1')
kp_manager = KeyPairManager(ec2_client)

# Create key pair
result = kp_manager.create_key_pair(
    key_name="my-keypair",
    save_path="my-keypair.pem"
)

print(f"Key Pair ID: {result['KeyPairId']}")
```

### modules/security_group.py

**Class**: `SecurityGroupManager`

**Purpose**: Manages EC2 security groups and ingress rules

**Methods**:

```python
__init__(ec2_client, ec2_resource)
    Initialize with boto3 clients

create_security_group(
    group_name: str,
    description: str,
    vpc_id: Optional[str] = None,
    tags: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]
    Create a new security group in specified VPC
    
add_ingress_rules(
    group_id: str,
    rules: List[Dict[str, Any]],
    my_ip: Optional[str] = None
) -> bool
    Add ingress rules to security group
    
delete_security_group(group_id: str) -> bool
    Delete a security group
```

**Rule Format**:
```python
rule = {
    "IpProtocol": "tcp",
    "FromPort": 22,
    "ToPort": 22,
    "CidrIp": "1.2.3.4/32",  # Optional, uses my_ip if not specified
    "Description": "SSH access"
}
```

### modules/ec2_instance.py

**Class**: `EC2InstanceManager`

**Purpose**: Manages EC2 instance lifecycle

**Methods**:

```python
__init__(ec2_client, ec2_resource)
    Initialize with boto3 clients

get_ami_id(ami_name_filter: str) -> str
    Find latest AMI matching filter pattern
    
create_instance(
    ami_id: str,
    instance_type: str,
    key_name: str,
    security_group_ids: List[str],
    user_data: str,
    instance_name: str,
    tags: Optional[List[Dict[str, str]]] = None,
    subnet_id: Optional[str] = None
) -> Dict[str, Any]
    Launch EC2 instance with specified configuration
    Automatically waits for instance to be running
    
get_instance_info(instance_id: str) -> Dict[str, Any]
    Retrieve instance details
    
terminate_instance(instance_id: str) -> bool
    Terminate an instance
    
get_instance_by_name(instance_name: str) -> Optional[Dict[str, Any]]
    Find instance by Name tag
```

### modules/alb.py

**Class**: `ALBManager`

**Purpose**: Manages Application Load Balancer, target groups, and listeners

**Methods**:

```python
__init__(elb_client, ec2_client)
    Initialize with boto3 clients

get_all_subnets(vpc_id: Optional[str] = None) -> List[str]
    Get all subnets in VPC (required for ALB)
    
create_target_group(
    name: str,
    vpc_id: str,
    port: int = 80,
    protocol: str = "HTTP",
    tags: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]
    Create target group for ALB
    
register_targets(
    target_group_arn: str,
    instance_ids: List[str]
) -> bool
    Register EC2 instances to target group
    
create_load_balancer(
    name: str,
    security_groups: List[str],
    subnets: List[str],
    tags: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]
    Create internet-facing Application Load Balancer
    Automatically waits for ALB to be available
    
create_listener(
    load_balancer_arn: str,
    target_group_arn: str,
    port: int = 80,
    protocol: str = "HTTP"
) -> Dict[str, Any]
    Create listener for load balancer
    
delete_load_balancer(load_balancer_arn: str) -> bool
    Delete load balancer
    
delete_target_group(target_group_arn: str) -> bool
    Delete target group
```

### utils/helpers.py

**Utility Functions**:

```python
get_my_public_ip() -> Optional[str]
    Retrieve public IP address of executing machine
    Uses AWS checkip service
    
format_tags(tags: list) -> list
    Format tags for AWS resources
    
print_section(title: str, width: int = 60) -> None
    Print formatted section header
    
print_resource_info(resource_type: str, resource_name: str, resource_id: str) -> None
    Print formatted resource information
    
print_error(message: str) -> None
    Print formatted error message
    
print_success(message: str) -> None
    Print formatted success message
    
wait_with_progress(message: str, seconds: int = 30) -> None
    Display waiting message with progress indicator
```

## Configuration Guide

### Basic Configuration

Edit `config.py` to customize your deployment:

**1. Template Selection**
```python
TEMPLATE_NAME = "barista-cafe"  # Resource naming prefix
TEMPLATE_ID = "2137"            # From tooplate.com
```

**2. AWS Settings**
```python
AWS_REGION = "us-east-1"        # Your AWS region
```

**3. Instance Configuration**
```python
INSTANCE_TYPE = "t2.micro"      # EC2 instance type
AMI_NAME_FILTER = "al2023-ami-2023.*-x86_64"  # AMI filter
```

### Advanced Configuration

**Custom User Data Script**:
```python
USER_DATA_SCRIPT = """#!/bin/bash
# Your custom initialization script
yum update -y
yum install -y httpd
# ... more commands
"""
```

**Security Group Rules**:
```python
INSTANCE_SG_RULES = [
    {
        "IpProtocol": "tcp",
        "FromPort": 22,
        "ToPort": 22,
        "Description": "SSH access"
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

**Resource Tags**:
```python
def get_tags() -> list:
    return [
        {"Key": "Project", "Value": TEMPLATE_NAME},
        {"Key": "Environment", "Value": "Production"},
        {"Key": "CostCenter", "Value": "Engineering"}
    ]
```

## Deployment Flow

### Step-by-Step Process

1. **Initialization**
   - Load configuration
   - Create Boto3 clients (EC2, ELBv2)
   - Initialize service managers

2. **Key Pair Creation**
   - Check if key pair exists
   - Create new key pair if needed
   - Save private key to .pem file
   - Set file permissions to 0400

3. **IP Address Resolution**
   - Query AWS checkip service
   - Store IP for security group rules
   - Fallback to None if unavailable

4. **Security Groups**
   - Get default VPC
   - Create instance security group
   - Add ingress rules (SSH from my IP, HTTP from anywhere)
   - Create ALB security group
   - Add ingress rules (HTTP from anywhere)

5. **EC2 Instance**
   - Query for latest Amazon Linux 2023 AMI
   - Launch instance with:
     - Selected AMI
     - Key pair
     - Security group
     - User data script
     - Auto-assign public IP enabled
   - Wait for instance to be running
   - Retrieve instance details

6. **ALB Infrastructure**
   - Get all subnets in VPC (multi-AZ requirement)
   - Create target group
   - Register EC2 instance to target group
   - Create Application Load Balancer
   - Wait for ALB to be available
   - Create listener on port 80
   - Forward traffic to target group

7. **Summary**
   - Display all created resources
   - Show access URLs
   - Print connection instructions

## Error Handling

### Exception Hierarchy

```
Exception
│
├─ ClientError (Boto3)
│  ├─ InvalidKeyPair.NotFound
│  ├─ InvalidGroup.NotFound
│  ├─ DuplicateTargetGroupName
│  ├─ DuplicateLoadBalancer
│  └─ DependencyViolation
│
├─ requests.RequestException
│  └─ Connection errors
│
└─ Custom Exceptions
   └─ Configuration errors
```

### Error Handling Strategies

**1. Resource Already Exists**
```python
try:
    response = self.ec2_client.create_key_pair(KeyName=key_name)
except ClientError as e:
    if e.response['Error']['Code'] == 'InvalidKeyPair.Duplicate':
        # Use existing key pair
        logger.info("Key pair already exists, using existing")
        return existing_key_pair_info
    raise
```

**2. Retry with Exponential Backoff**
```python
max_retries = 5
for attempt in range(max_retries):
    try:
        self.ec2_client.delete_security_group(GroupId=sg_id)
        break
    except ClientError as e:
        if e.response['Error']['Code'] == 'DependencyViolation':
            time.sleep(10 * (attempt + 1))  # Exponential backoff
        else:
            raise
```

**3. Graceful Degradation**
```python
my_ip = get_my_public_ip()
if not my_ip:
    logger.warning("Failed to get public IP, SSH rule will not be added")
    # Continue without SSH rule instead of failing
```

## Security Considerations

### 1. Credential Management
- Never hardcode AWS credentials
- Use AWS CLI configuration or environment variables
- Use IAM roles when running on EC2

### 2. Key Pair Protection
```python
# Private key saved with restricted permissions
os.chmod(save_path, 0o400)  # Read-only for owner
```

### 3. Security Group Best Practices
- SSH access restricted to specific IP
- HTTP access from anywhere (public website)
- No unnecessary ports exposed
- Descriptive rule descriptions

### 4. IAM Permissions Required

Minimum IAM policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*",
                "ec2:CreateKeyPair",
                "ec2:CreateSecurityGroup",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:RunInstances",
                "ec2:CreateTags",
                "elasticloadbalancing:CreateLoadBalancer",
                "elasticloadbalancing:CreateTargetGroup",
                "elasticloadbalancing:CreateListener",
                "elasticloadbalancing:RegisterTargets"
            ],
            "Resource": "*"
        }
    ]
}
```

### 5. Resource Tagging
```python
tags = [
    {"Key": "Project", "Value": TEMPLATE_NAME},
    {"Key": "ManagedBy", "Value": "Boto3-Automation"},
    {"Key": "Environment", "Value": "Demo"}
]
```
- Enables cost tracking
- Facilitates resource management
- Supports compliance requirements

### 6. Cleanup Procedure
- Always clean up resources when done
- Avoid orphaned resources
- Check for dependencies before deletion
- Use `cleanup.py` script

---

**Last Updated**: December 2025
**Version**: 1.0.0
