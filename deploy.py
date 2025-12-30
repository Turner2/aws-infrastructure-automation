"""
Main deployment script for AWS infrastructure.

This script orchestrates the deployment of:
- EC2 Key Pair
- Security Groups (for EC2 and ALB)
- EC2 Instance with web server
- Application Load Balancer with Target Group
"""

import sys
import logging
import boto3
from botocore.exceptions import ClientError

# Import local modules
from config import (
    AWS_REGION,
    INSTANCE_TYPE,
    AMI_NAME_FILTER,
    get_resource_names,
    get_user_data,
    get_tags,
    INSTANCE_SG_RULES,
    ALB_SG_RULES,
    TEMPLATE_NAME
)
from modules import (
    KeyPairManager,
    SecurityGroupManager,
    EC2InstanceManager,
    ALBManager
)
from utils import (
    get_my_public_ip,
    print_section,
    print_resource_info,
    print_error,
    print_success,
    wait_with_progress
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InfrastructureDeployer:
    """Manages the deployment of AWS infrastructure."""
    
    def __init__(self, region: str = AWS_REGION):
        """
        Initialize the deployer.
        
        Args:
            region: AWS region to deploy to
        """
        self.region = region
        self.resource_names = get_resource_names()
        self.tags = get_tags()
        
        # Initialize AWS clients
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.ec2_resource = boto3.resource('ec2', region_name=region)
        self.elb_client = boto3.client('elbv2', region_name=region)
        
        # Initialize managers
        self.keypair_manager = KeyPairManager(self.ec2_client)
        self.sg_manager = SecurityGroupManager(self.ec2_client, self.ec2_resource)
        self.instance_manager = EC2InstanceManager(self.ec2_client, self.ec2_resource)
        self.alb_manager = ALBManager(self.elb_client, self.ec2_client)
        
        # Store created resources
        self.resources = {}
    
    def deploy(self):
        """Execute the full deployment."""
        try:
            print_section("AWS Infrastructure Deployment")
            print(f"Region: {self.region}")
            print(f"Template: {TEMPLATE_NAME}")
            print()
            
            # Step 1: Create Key Pair
            self._create_key_pair()
            
            # Step 2: Get My IP
            self._get_my_ip()
            
            # Step 3: Create Security Groups
            self._create_security_groups()
            
            # Step 4: Create EC2 Instance
            self._create_ec2_instance()
            
            # Step 5: Create ALB Infrastructure
            self._create_alb_infrastructure()
            
            # Step 6: Print Summary
            self._print_deployment_summary()
            
            print_success("\nDeployment completed successfully!")
            
        except Exception as e:
            print_error(f"Deployment failed: {e}")
            logger.exception("Deployment failed")
            sys.exit(1)
    
    def _create_key_pair(self):
        """Create EC2 key pair."""
        print_section("1. Creating Key Pair")
        
        key_name = self.resource_names["key_pair"]
        key_file = f"{key_name}.pem"
        
        result = self.keypair_manager.create_key_pair(
            key_name=key_name,
            save_path=key_file
        )
        
        self.resources["key_pair"] = result
        print_resource_info("Key Pair", key_name, result["KeyPairId"])
        
        if not result.get("Exists"):
            print(f"  Private key saved to: {key_file}")
            print(f"  Keep this file safe! It cannot be recovered.")
    
    def _get_my_ip(self):
        """Get public IP address."""
        print_section("2. Getting Public IP Address")
        
        my_ip = get_my_public_ip()
        if not my_ip:
            print_error("Failed to retrieve public IP. SSH access will not be configured.")
            my_ip = None
        else:
            print(f"✓ Your public IP: {my_ip}")
        
        self.resources["my_ip"] = my_ip
    
    def _create_security_groups(self):
        """Create security groups for EC2 and ALB."""
        print_section("3. Creating Security Groups")
        
        # Create instance security group
        print("\nCreating EC2 Security Group...")
        instance_sg = self.sg_manager.create_security_group(
            group_name=self.resource_names["security_group"],
            description=f"Security group for {TEMPLATE_NAME} EC2 instance",
            tags=self.tags
        )
        
        # Add ingress rules
        self.sg_manager.add_ingress_rules(
            group_id=instance_sg["GroupId"],
            rules=INSTANCE_SG_RULES,
            my_ip=self.resources.get("my_ip")
        )
        
        self.resources["instance_sg"] = instance_sg
        print_resource_info("Instance SG", instance_sg["GroupName"], instance_sg["GroupId"])
        
        # Create ALB security group
        print("\nCreating ALB Security Group...")
        alb_sg = self.sg_manager.create_security_group(
            group_name=self.resource_names["alb_sg"],
            description=f"Security group for {TEMPLATE_NAME} ALB",
            tags=self.tags
        )
        
        # Add ALB ingress rules
        self.sg_manager.add_ingress_rules(
            group_id=alb_sg["GroupId"],
            rules=ALB_SG_RULES
        )
        
        self.resources["alb_sg"] = alb_sg
        print_resource_info("ALB SG", alb_sg["GroupName"], alb_sg["GroupId"])
    
    def _create_ec2_instance(self):
        """Create EC2 instance."""
        print_section("4. Launching EC2 Instance")
        
        # Get AMI ID
        print("Finding latest Amazon Linux 2023 AMI...")
        ami_id = self.instance_manager.get_ami_id(AMI_NAME_FILTER)
        print(f"✓ Using AMI: {ami_id}")
        
        # Create instance
        print(f"\nLaunching {INSTANCE_TYPE} instance...")
        instance_info = self.instance_manager.create_instance(
            ami_id=ami_id,
            instance_type=INSTANCE_TYPE,
            key_name=self.resource_names["key_pair"],
            security_group_ids=[self.resources["instance_sg"]["GroupId"]],
            user_data=get_user_data(),
            instance_name=self.resource_names["instance"],
            tags=self.tags
        )
        
        self.resources["instance"] = instance_info
        print_resource_info("Instance", self.resource_names["instance"], instance_info["InstanceId"])
        print(f"  Public IP: {instance_info['PublicIpAddress']}")
        print(f"  Private IP: {instance_info['PrivateIpAddress']}")
        print(f"  Availability Zone: {instance_info['AvailabilityZone']}")
        
        print("\nWebsite is being set up (this takes ~2-3 minutes)...")
    
    def _create_alb_infrastructure(self):
        """Create Application Load Balancer and related resources."""
        print_section("5. Creating Application Load Balancer")
        
        # Get VPC ID from instance
        vpc_id = self.resources["instance"]["VpcId"]
        
        # Get all subnets
        print("Finding subnets across all availability zones...")
        subnets = self.alb_manager.get_all_subnets(vpc_id)
        print(f"✓ Found {len(subnets)} subnets")
        
        # Create target group
        print("\nCreating Target Group...")
        target_group = self.alb_manager.create_target_group(
            name=self.resource_names["target_group"],
            vpc_id=vpc_id,
            tags=self.tags
        )
        
        self.resources["target_group"] = target_group
        print_resource_info("Target Group", target_group["TargetGroupName"], target_group["TargetGroupArn"].split('/')[-1])
        
        # Register instance to target group
        print("\nRegistering instance to target group...")
        self.alb_manager.register_targets(
            target_group_arn=target_group["TargetGroupArn"],
            instance_ids=[self.resources["instance"]["InstanceId"]]
        )
        print("✓ Instance registered")
        
        # Create load balancer
        print("\nCreating Application Load Balancer...")
        load_balancer = self.alb_manager.create_load_balancer(
            name=self.resource_names["alb"],
            security_groups=[self.resources["alb_sg"]["GroupId"]],
            subnets=subnets,
            tags=self.tags
        )
        
        self.resources["load_balancer"] = load_balancer
        print_resource_info("Load Balancer", load_balancer["LoadBalancerName"], load_balancer["LoadBalancerArn"].split('/')[-1])
        
        # Create listener
        print("\nCreating Listener...")
        listener = self.alb_manager.create_listener(
            load_balancer_arn=load_balancer["LoadBalancerArn"],
            target_group_arn=target_group["TargetGroupArn"]
        )
        
        self.resources["listener"] = listener
        print("✓ Listener created on port 80")
    
    def _print_deployment_summary(self):
        """Print deployment summary."""
        print_section("Deployment Summary")
        
        print("\nKey Pair:")
        print(f"   Name: {self.resource_names['key_pair']}")
        print(f"   File: {self.resource_names['key_pair']}.pem")
        
        print("\nSecurity Groups:")
        print(f"   Instance SG: {self.resources['instance_sg']['GroupId']}")
        print(f"   ALB SG: {self.resources['alb_sg']['GroupId']}")
        
        print("\nEC2 Instance:")
        print(f"   ID: {self.resources['instance']['InstanceId']}")
        print(f"   Type: {INSTANCE_TYPE}")
        print(f"   Public IP: {self.resources['instance']['PublicIpAddress']}")
        
        print("\nLoad Balancer:")
        print(f"   Name: {self.resources['load_balancer']['LoadBalancerName']}")
        print(f"   DNS: {self.resources['load_balancer']['DNSName']}")
        
        print("\n" + "="*60)
        print("ACCESS YOUR WEBSITE:")
        print("="*60)
        print(f"\n   ALB Endpoint: http://{self.resources['load_balancer']['DNSName']}")
        print(f"   Direct Access: http://{self.resources['instance']['PublicIpAddress']}")
        print(f"   Instance Info: http://{self.resources['load_balancer']['DNSName']}/instance-info.html")
        print("\nNote: Allow 2-3 minutes for the website to be fully configured.")
        print("="*60)


def main():
    """Main entry point."""
    try:
        deployer = InfrastructureDeployer()
        deployer.deploy()
    except KeyboardInterrupt:
        print("\n\nDeployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Fatal error: {e}")
        logger.exception("Fatal error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()
