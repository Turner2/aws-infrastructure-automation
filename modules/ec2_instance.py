"""
AWS EC2 Instance management module.
"""

import logging
from typing import Dict, Any, Optional, List
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class EC2InstanceManager:
    """Manages AWS EC2 Instances."""
    
    def __init__(self, ec2_client, ec2_resource):
        """
        Initialize EC2InstanceManager.
        
        Args:
            ec2_client: Boto3 EC2 client
            ec2_resource: Boto3 EC2 resource
        """
        self.ec2_client = ec2_client
        self.ec2_resource = ec2_resource
    
    def get_ami_id(self, ami_name_filter: str) -> str:
        """
        Get the latest AMI ID matching the filter.
        
        Args:
            ami_name_filter: Name filter for AMI (e.g., 'al2023-ami-*')
            
        Returns:
            str: AMI ID
        """
        try:
            response = self.ec2_client.describe_images(
                Filters=[
                    {"Name": "name", "Values": [ami_name_filter]},
                    {"Name": "state", "Values": ["available"]},
                    {"Name": "architecture", "Values": ["x86_64"]}
                ],
                Owners=["amazon"]
            )
            
            if not response["Images"]:
                raise Exception(f"No AMI found matching filter: {ami_name_filter}")
            
            # Sort by creation date and get the latest
            images = sorted(
                response["Images"],
                key=lambda x: x["CreationDate"],
                reverse=True
            )
            
            ami_id = images[0]["ImageId"]
            ami_name = images[0]["Name"]
            logger.info(f"Found AMI: {ami_name} ({ami_id})")
            
            return ami_id
            
        except ClientError as e:
            logger.error(f"Failed to get AMI: {e}")
            raise
    
    def create_instance(
        self,
        ami_id: str,
        instance_type: str,
        key_name: str,
        security_group_ids: List[str],
        user_data: str,
        instance_name: str,
        tags: Optional[List[Dict[str, str]]] = None,
        subnet_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an EC2 instance.
        
        Args:
            ami_id: AMI ID to use
            instance_type: Instance type (e.g., 't2.micro')
            key_name: Key pair name
            security_group_ids: List of security group IDs
            user_data: User data script
            instance_name: Name tag for the instance
            tags: Optional additional tags
            subnet_id: Optional subnet ID
            
        Returns:
            dict: Instance information
        """
        try:
            # Prepare tags
            all_tags = [{"Key": "Name", "Value": instance_name}]
            if tags:
                all_tags.extend(tags)
            
            # Prepare instance parameters
            params = {
                "ImageId": ami_id,
                "InstanceType": instance_type,
                "KeyName": key_name,
                "SecurityGroupIds": security_group_ids,
                "UserData": user_data,
                "MinCount": 1,
                "MaxCount": 1,
                "TagSpecifications": [{
                    "ResourceType": "instance",
                    "Tags": all_tags
                }],
                "NetworkInterfaces": [{
                    "AssociatePublicIpAddress": True,
                    "DeviceIndex": 0,
                    "Groups": security_group_ids
                }]
            }
            
            # Add subnet if specified
            if subnet_id:
                params["NetworkInterfaces"][0]["SubnetId"] = subnet_id
            
            # Launch instance
            response = self.ec2_client.run_instances(**params)
            instance = response["Instances"][0]
            instance_id = instance["InstanceId"]
            
            logger.info(f"Launched instance: {instance_id}")
            
            # Wait for instance to be running
            logger.info(f"Waiting for instance {instance_id} to be running...")
            waiter = self.ec2_client.get_waiter('instance_running')
            waiter.wait(InstanceIds=[instance_id])
            
            logger.info(f"Instance {instance_id} is now running")
            
            # Get updated instance information
            instance_info = self.get_instance_info(instance_id)
            
            return instance_info
            
        except ClientError as e:
            logger.error(f"Failed to create instance: {e}")
            raise
    
    def get_instance_info(self, instance_id: str) -> Dict[str, Any]:
        """
        Get instance information.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            dict: Instance information
        """
        try:
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            instance = response["Reservations"][0]["Instances"][0]
            
            return {
                "InstanceId": instance_id,
                "InstanceType": instance["InstanceType"],
                "State": instance["State"]["Name"],
                "PublicIpAddress": instance.get("PublicIpAddress"),
                "PrivateIpAddress": instance.get("PrivateIpAddress"),
                "AvailabilityZone": instance["Placement"]["AvailabilityZone"],
                "SubnetId": instance.get("SubnetId"),
                "VpcId": instance.get("VpcId")
            }
            
        except ClientError as e:
            logger.error(f"Failed to get instance info: {e}")
            raise
    
    def terminate_instance(self, instance_id: str) -> bool:
        """
        Terminate an EC2 instance.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            bool: True if successful
        """
        try:
            self.ec2_client.terminate_instances(InstanceIds=[instance_id])
            logger.info(f"Terminated instance: {instance_id}")
            return True
        except ClientError as e:
            logger.error(f"Failed to terminate instance: {e}")
            return False
    
    def get_instance_by_name(self, instance_name: str) -> Optional[Dict[str, Any]]:
        """
        Get instance by name tag.
        
        Args:
            instance_name: Instance name
            
        Returns:
            dict: Instance information or None if not found
        """
        try:
            response = self.ec2_client.describe_instances(
                Filters=[
                    {"Name": "tag:Name", "Values": [instance_name]},
                    {"Name": "instance-state-name", "Values": ["running", "pending", "stopped"]}
                ]
            )
            
            if response["Reservations"]:
                instance = response["Reservations"][0]["Instances"][0]
                return self.get_instance_info(instance["InstanceId"])
            
            return None
            
        except ClientError as e:
            logger.error(f"Failed to get instance by name: {e}")
            return None
