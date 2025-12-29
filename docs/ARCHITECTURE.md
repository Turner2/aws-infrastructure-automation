# AWS Infrastructure Architecture Diagram

## Overall Architecture

```
                           Internet
                              │
                              ▼
                    ┌─────────────────┐
                    │  Route 53 DNS   │ (Optional - Future Enhancement)
                    └────────┬─────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │   Application Load Balancer (ALB)      │
        │   - Internet-facing                    │
        │   - Port 80 (HTTP)                     │
        │   - Multi-AZ (High Availability)       │
        │   - Health Checks Enabled              │
        └──────────┬──────────────────────────────┘
                   │
                   │ Forward Traffic
                   ▼
        ┌─────────────────────────────────┐
        │      Target Group               │
        │   - Health Check: /             │
        │   - Interval: 30s               │
        │   - Timeout: 5s                 │
        │   - Healthy Threshold: 2        │
        │   - Unhealthy Threshold: 2      │
        └──────────┬───────────────────────┘
                   │
                   │ Route to Healthy Targets
                   ▼
        ┌──────────────────────────────────┐
        │     EC2 Instance                 │
        │   - Type: t2.micro               │
        │   - OS: Amazon Linux 2023        │
        │   - Auto-assign Public IP: Yes   │
        │   - Apache Web Server            │
        │   - Website from Tooplate        │
        └──────────┬───────────────────────┘
                   │
                   │ Protected by
                   ▼
        ┌──────────────────────────────────┐
        │   Security Groups                │
        │                                  │
        │   EC2 Security Group:            │
        │   - SSH (Port 22) from My IP     │
        │   - HTTP (Port 80) from 0.0.0.0/0│
        │                                  │
        │   ALB Security Group:            │
        │   - HTTP (Port 80) from 0.0.0.0/0│
        └──────────────────────────────────┘
```

## Deployment Flow Diagram

```
START
  │
  ▼
┌─────────────────────────┐
│ Initialize Boto3 Clients│
│ - EC2 Client            │
│ - ELB Client            │
│ - EC2 Resource          │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Create Key Pair         │
│ - Generate new key      │
│ - Save to .pem file     │
│ - Set permissions 0400  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Get Public IP           │
│ - Query AWS checkip     │
│ - Store for SG rules    │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Create Security Groups  │
│                         │
│ Instance SG:            │
│ - SSH from my IP        │
│ - HTTP from anywhere    │
│                         │
│ ALB SG:                 │
│ - HTTP from anywhere    │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Find Latest AMI         │
│ - Filter: AL2023        │
│ - Sort by date          │
│ - Select newest         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Launch EC2 Instance     │
│ - Apply user data       │
│ - Attach security group │
│ - Enable public IP      │
│ - Wait for running      │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Setup Web Server        │
│ (User Data Script)      │
│ - Install Apache        │
│ - Download template     │
│ - Configure website     │
│ - Start services        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Get Subnets             │
│ - Query VPC             │
│ - Get all subnets       │
│ - Ensure multi-AZ       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Create Target Group     │
│ - Configure health check│
│ - Set target type       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Register Target         │
│ - Add EC2 instance      │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Create Load Balancer    │
│ - Internet-facing       │
│ - Multi-AZ deployment   │
│ - Wait for active       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Create Listener         │
│ - Port 80 (HTTP)        │
│ - Forward to TG         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Display Summary         │
│ - Resource IDs          │
│ - Access URLs           │
│ - Connection info       │
└────────┬────────────────┘
         │
         ▼
       END
```

## Module Interaction Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    InfrastructureDeployer                │
│                   (Main Orchestrator)                    │
└──┬──────────────┬──────────────┬──────────────┬────────┘
   │              │              │              │
   │              │              │              │
   ▼              ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌───────────┐  ┌────────┐
│KeyPair  │  │Security  │  │  EC2      │  │  ALB   │
│Manager  │  │Group     │  │ Instance  │  │Manager │
│         │  │Manager   │  │ Manager   │  │        │
└────┬────┘  └─────┬────┘  └─────┬─────┘  └───┬────┘
     │             │              │            │
     │             │              │            │
     ▼             ▼              ▼            ▼
  ┌────────────────────────────────────────────────┐
  │            Boto3 AWS SDK                       │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
  │  │EC2 Client│  │EC2       │  │ELBv2     │    │
  │  │          │  │Resource  │  │Client    │    │
  │  └──────────┘  └──────────┘  └──────────┘    │
  └──────────────────┬─────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   AWS Services       │
          │   - EC2              │
          │   - ELB              │
          │   - VPC              │
          └──────────────────────┘
```

## Data Flow - Create Instance

```
User Code
   │
   │ call create_instance()
   ▼
EC2InstanceManager
   │
   │ 1. Prepare parameters
   │ 2. Configure network interface
   │ 3. Set public IP assignment
   │ 4. Format user data
   ▼
EC2 Client (Boto3)
   │
   │ run_instances()
   ▼
AWS EC2 API
   │
   │ Creates instance
   │ Assigns resources
   │ Starts instance
   ▼
Instance Waiter
   │
   │ get_waiter('instance_running')
   │ Polls status every few seconds
   ▼
Instance Running
   │
   │ Executes user data script
   │ Configures web server
   ▼
Return Instance Info
   │
   │ - Instance ID
   │ - Public IP
   │ - Private IP
   │ - Availability Zone
   ▼
Back to User Code
```

## Error Handling Flow

```
Try AWS Operation
     │
     ▼
  Success?
     │
     ├─ Yes ─► Return Result
     │
     └─ No ──► ClientError
                   │
                   ▼
              Check Error Code
                   │
                   ├─ ResourceExists ──► Use Existing ──► Continue
                   │
                   ├─ DependencyViolation ──► Retry with Backoff
                   │                               │
                   │                               ▼
                   │                          Success? ─► Continue
                   │                               │
                   │                               └─ No ─► Raise Error
                   │
                   ├─ InvalidParameter ──► Log Error ──► Raise
                   │
                   └─ Other ──► Log Exception ──► Raise
```

## Network Architecture

```
┌───────────────────────────────────────────────────────────┐
│                        VPC (Default)                       │
│                                                           │
│  ┌─────────────────────┐    ┌─────────────────────┐     │
│  │   Subnet 1          │    │   Subnet 2          │     │
│  │   (AZ: us-east-1a)  │    │   (AZ: us-east-1b)  │     │
│  │                     │    │                     │     │
│  │  ┌──────────────┐   │    │                     │     │
│  │  │ EC2 Instance │   │    │  (Available for     │     │
│  │  │              │   │    │   scaling)          │     │
│  │  └──────────────┘   │    │                     │     │
│  │                     │    │                     │     │
│  └─────────────────────┘    └─────────────────────┘     │
│              │                        │                  │
│              └────────────┬───────────┘                  │
│                           │                              │
│                  ┌────────▼────────┐                     │
│                  │ Target Group    │                     │
│                  └────────┬────────┘                     │
│                           │                              │
│                  ┌────────▼────────┐                     │
│                  │  Load Balancer  │                     │
│                  └────────┬────────┘                     │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
                       Internet
```

## Security Group Rules Visualization

```
┌─────────────────────────────────────────────────────────┐
│              Instance Security Group                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Inbound Rules:                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Rule 1: SSH (Port 22)                             │ │
│  │ Source: YOUR_IP/32                                │ │
│  │ Description: SSH access from my IP                │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Rule 2: HTTP (Port 80)                            │ │
│  │ Source: 0.0.0.0/0                                 │ │
│  │ Description: HTTP access from anywhere            │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  Outbound Rules:                                        │
│  ┌───────────────────────────────────────────────────┐ │
│  │ All Traffic                                       │ │
│  │ Destination: 0.0.0.0/0                            │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                ALB Security Group                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Inbound Rules:                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Rule 1: HTTP (Port 80)                            │ │
│  │ Source: 0.0.0.0/0                                 │ │
│  │ Description: HTTP access from anywhere            │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  Outbound Rules:                                        │
│  ┌───────────────────────────────────────────────────┐ │
│  │ All Traffic                                       │ │
│  │ Destination: 0.0.0.0/0                            │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## User Data Script Flow

```
Instance Starts
     │
     ▼
Execute User Data
     │
     ├─► Update System Packages
     │   └─► yum update -y
     │
     ├─► Install Apache & Tools
     │   └─► yum install -y httpd wget unzip
     │
     ├─► Start Apache Service
     │   ├─► systemctl start httpd
     │   └─► systemctl enable httpd
     │
     ├─► Download Template
     │   ├─► wget tooplate.com/zip-templates/{id}.zip
     │   ├─► unzip template
     │   └─► cp files to /var/www/html/
     │
     ├─► Create Instance Info Page
     │   └─► Generate instance-info.html
     │
     ├─► Set Permissions
     │   ├─► chown -R apache:apache
     │   └─► chmod -R 755
     │
     └─► Restart Apache
         └─► systemctl restart httpd
              │
              ▼
         Website Ready!
```

---

These diagrams help visualize:
1. Overall architecture and component relationships
2. Step-by-step deployment process
3. Module interactions
4. Data flow through the system
5. Error handling strategies
6. Network topology
7. Security configurations
8. Initialization procedures

Use these diagrams when:
- Explaining the project in interviews
- Documenting new features
- Troubleshooting issues
- Training new contributors
- Creating presentations
