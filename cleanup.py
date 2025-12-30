"""
Cleanup script to remove all AWS resources created by the deployment.
"""

import sys
import logging
import boto3
from botocore.exceptions import ClientError
import time

from config import get_resource_names, AWS_REGION
from utils import print_section, print_success, print_error

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InfrastructureCleaner:
    """Cleans up AWS resources."""
    
    def __init__(self, region: str = AWS_REGION):
        """
        Initialize the cleaner.
        
        Args:
            region: AWS region
        """
        self.region = region
        self.resource_names = get_resource_names()
        
        # Initialize AWS clients
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.elb_client = boto3.client('elbv2', region_name=region)
    
    def cleanup(self, skip_confirmation: bool = False):
        """Execute the cleanup."""
        try:
            print_section("AWS Infrastructure Cleanup")
            
            if not skip_confirmation:
                print("\nWARNING: This will delete the following resources:")
                print(f"   - Load Balancer: {self.resource_names['alb']}")
                print(f"   - Target Group: {self.resource_names['target_group']}")
                print(f"   - EC2 Instance: {self.resource_names['instance']}")
                print(f"   - Security Groups: {self.resource_names['security_group']}, {self.resource_names['alb_sg']}")
                print(f"   - Key Pair: {self.resource_names['key_pair']}")
                
                response = input("\nAre you sure you want to continue? (yes/no): ")
                if response.lower() != 'yes':
                    print("Cleanup cancelled.")
                    return
            
            # Step 1: Delete Load Balancer
            self._delete_load_balancer()
            
            # Step 2: Delete Target Group (wait for LB deletion)
            time.sleep(10)  # Wait for LB to start deleting
            self._delete_target_group()
            
            # Step 3: Terminate EC2 Instance
            self._terminate_instance()
            
            # Step 4: Delete Security Groups (wait for instance termination)
            self._delete_security_groups()
            
            # Step 5: Delete Key Pair
            self._delete_key_pair()
            
            print_success("\nCleanup completed successfully!")
            
        except Exception as e:
            print_error(f"Cleanup failed: {e}")
            logger.exception("Cleanup failed")
            sys.exit(1)
    
    def _delete_load_balancer(self):
        """Delete Application Load Balancer."""
        print_section("1. Deleting Load Balancer")
        
        try:
            # Find load balancer
            response = self.elb_client.describe_load_balancers(
                Names=[self.resource_names["alb"]]
            )
            
            if not response["LoadBalancers"]:
                print("Load balancer not found, skipping...")
                return
            
            lb_arn = response["LoadBalancers"][0]["LoadBalancerArn"]
            
            # Delete load balancer
            self.elb_client.delete_load_balancer(LoadBalancerArn=lb_arn)
            print(f"✓ Deleted load balancer: {self.resource_names['alb']}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'LoadBalancerNotFound':
                print("Load balancer not found, skipping...")
            else:
                logger.error(f"Failed to delete load balancer: {e}")
    
    def _delete_target_group(self):
        """Delete Target Group."""
        print_section("2. Deleting Target Group")
        
        try:
            # Find target group
            response = self.elb_client.describe_target_groups(
                Names=[self.resource_names["target_group"]]
            )
            
            if not response["TargetGroups"]:
                print("Target group not found, skipping...")
                return
            
            tg_arn = response["TargetGroups"][0]["TargetGroupArn"]
            
            # Wait a bit more for load balancer to be fully deleted
            print("Waiting for load balancer deletion to complete...")
            time.sleep(20)
            
            # Delete target group
            self.elb_client.delete_target_group(TargetGroupArn=tg_arn)
            print(f"✓ Deleted target group: {self.resource_names['target_group']}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'TargetGroupNotFound':
                print("Target group not found, skipping...")
            else:
                logger.warning(f"Failed to delete target group: {e}")
                print("Target group might still be in use. Try again in a few minutes.")
    
    def _terminate_instance(self):
        """Terminate EC2 Instance."""
        print_section("3. Terminating EC2 Instance")
        
        try:
            # Find instance
            response = self.ec2_client.describe_instances(
                Filters=[
                    {"Name": "tag:Name", "Values": [self.resource_names["instance"]]},
                    {"Name": "instance-state-name", "Values": ["running", "stopped", "stopping", "pending"]}
                ]
            )
            
            if not response["Reservations"]:
                print("Instance not found, skipping...")
                return
            
            instance_id = response["Reservations"][0]["Instances"][0]["InstanceId"]
            
            # Terminate instance
            self.ec2_client.terminate_instances(InstanceIds=[instance_id])
            print(f"✓ Terminated instance: {instance_id}")
            
            # Wait for termination
            print("Waiting for instance to terminate...")
            waiter = self.ec2_client.get_waiter('instance_terminated')
            waiter.wait(InstanceIds=[instance_id])
            print("✓ Instance terminated")
            
        except ClientError as e:
            logger.error(f"Failed to terminate instance: {e}")
    
    def _delete_security_groups(self):
        """Delete Security Groups."""
        print_section("4. Deleting Security Groups")
        
        for sg_name in [self.resource_names["security_group"], self.resource_names["alb_sg"]]:
            try:
                # Find security group
                response = self.ec2_client.describe_security_groups(
                    Filters=[{"Name": "group-name", "Values": [sg_name]}]
                )
                
                if not response["SecurityGroups"]:
                    print(f"Security group '{sg_name}' not found, skipping...")
                    continue
                
                sg_id = response["SecurityGroups"][0]["GroupId"]
                
                # Delete security group (with retry for dependencies)
                max_retries = 5
                for attempt in range(max_retries):
                    try:
                        self.ec2_client.delete_security_group(GroupId=sg_id)
                        print(f"✓ Deleted security group: {sg_name}")
                        break
                    except ClientError as e:
                        if e.response['Error']['Code'] == 'DependencyViolation' and attempt < max_retries - 1:
                            print(f"Waiting for dependencies to clear (attempt {attempt + 1}/{max_retries})...")
                            time.sleep(10)
                        else:
                            raise
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'InvalidGroup.NotFound':
                    print(f"Security group '{sg_name}' not found, skipping...")
                else:
                    logger.warning(f"Failed to delete security group '{sg_name}': {e}")
    
    def _delete_key_pair(self):
        """Delete Key Pair."""
        print_section("5. Deleting Key Pair")
        
        try:
            self.ec2_client.delete_key_pair(KeyName=self.resource_names["key_pair"])
            print(f"✓ Deleted key pair: {self.resource_names['key_pair']}")
            print(f"Remember to manually delete the .pem file: {self.resource_names['key_pair']}.pem")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidKeyPair.NotFound':
                print("Key pair not found, skipping...")
            else:
                logger.error(f"Failed to delete key pair: {e}")


def main():
    """Main entry point."""
    try:
        cleaner = InfrastructureCleaner()
        
        # Check for --force flag
        skip_confirmation = '--force' in sys.argv
        
        cleaner.cleanup(skip_confirmation=skip_confirmation)
        
    except KeyboardInterrupt:
        print("\n\nCleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Fatal error: {e}")
        logger.exception("Fatal error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()
