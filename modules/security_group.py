"""
AWS Security Group management module.
"""

import logging
from typing import List, Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class SecurityGroupManager:
    """Manages AWS EC2 Security Groups."""
    
    def __init__(self, ec2_client, ec2_resource):
        """
        Initialize SecurityGroupManager.
        
        Args:
            ec2_client: Boto3 EC2 client
            ec2_resource: Boto3 EC2 resource
        """
        self.ec2_client = ec2_client
        self.ec2_resource = ec2_resource
    
    def create_security_group(
        self,
        group_name: str,
        description: str,
        vpc_id: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Create a security group.
        
        Args:
            group_name: Name of the security group
            description: Description of the security group
            vpc_id: VPC ID (uses default if not specified)
            tags: Optional tags for the security group
            
        Returns:
            dict: Security group information
        """
        try:
            # Check if security group already exists
            try:
                response = self.ec2_client.describe_security_groups(
                    GroupNames=[group_name]
                )
                logger.info(f"Security group '{group_name}' already exists")
                return {
                    "GroupId": response["SecurityGroups"][0]["GroupId"],
                    "GroupName": group_name,
                    "Exists": True
                }
            except ClientError as e:
                if e.response['Error']['Code'] != 'InvalidGroup.NotFound':
                    raise
            
            # Get default VPC if not specified
            if not vpc_id:
                vpc_id = self._get_default_vpc()
            
            # Create security group
            params = {
                "GroupName": group_name,
                "Description": description,
                "VpcId": vpc_id
            }
            
            if tags:
                params["TagSpecifications"] = [{
                    "ResourceType": "security-group",
                    "Tags": tags
                }]
            
            response = self.ec2_client.create_security_group(**params)
            group_id = response["GroupId"]
            logger.info(f"Created security group: {group_name} ({group_id})")
            
            return {
                "GroupId": group_id,
                "GroupName": group_name,
                "VpcId": vpc_id,
                "Exists": False
            }
            
        except ClientError as e:
            logger.error(f"Failed to create security group: {e}")
            raise
    
    def add_ingress_rules(
        self,
        group_id: str,
        rules: List[Dict[str, Any]],
        my_ip: Optional[str] = None
    ) -> bool:
        """
        Add ingress rules to a security group.
        
        Args:
            group_id: Security group ID
            rules: List of rule dictionaries
            my_ip: Optional IP address to use for rules that need it
            
        Returns:
            bool: True if successful
        """
        try:
            permissions = []
            
            for rule in rules:
                permission = {
                    "IpProtocol": rule["IpProtocol"],
                    "FromPort": rule["FromPort"],
                    "ToPort": rule["ToPort"]
                }
                
                # Add description if provided
                if "Description" in rule:
                    permission["IpRanges"] = [{"Description": rule["Description"]}]
                
                # Use specific CIDR or my_ip
                if "CidrIp" in rule:
                    if "IpRanges" in permission:
                        permission["IpRanges"][0]["CidrIp"] = rule["CidrIp"]
                    else:
                        permission["IpRanges"] = [{"CidrIp": rule["CidrIp"]}]
                elif my_ip:
                    cidr = f"{my_ip}/32"
                    if "IpRanges" in permission:
                        permission["IpRanges"][0]["CidrIp"] = cidr
                    else:
                        permission["IpRanges"] = [{"CidrIp": cidr}]
                
                permissions.append(permission)
            
            # Add rules to security group
            self.ec2_client.authorize_security_group_ingress(
                GroupId=group_id,
                IpPermissions=permissions
            )
            
            logger.info(f"Added {len(permissions)} ingress rules to {group_id}")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidPermission.Duplicate':
                logger.warning(f"Some rules already exist in {group_id}")
                return True
            logger.error(f"Failed to add ingress rules: {e}")
            return False
    
    def delete_security_group(self, group_id: str) -> bool:
        """
        Delete a security group.
        
        Args:
            group_id: Security group ID
            
        Returns:
            bool: True if successful
        """
        try:
            self.ec2_client.delete_security_group(GroupId=group_id)
            logger.info(f"Deleted security group: {group_id}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete security group: {e}")
            return False
    
    def _get_default_vpc(self) -> str:
        """
        Get the default VPC ID.
        
        Returns:
            str: Default VPC ID
        """
        try:
            response = self.ec2_client.describe_vpcs(
                Filters=[{"Name": "isDefault", "Values": ["true"]}]
            )
            if response["Vpcs"]:
                vpc_id = response["Vpcs"][0]["VpcId"]
                logger.info(f"Using default VPC: {vpc_id}")
                return vpc_id
            raise Exception("No default VPC found")
        except ClientError as e:
            logger.error(f"Failed to get default VPC: {e}")
            raise
