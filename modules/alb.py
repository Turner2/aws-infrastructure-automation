"""
AWS Application Load Balancer management module.
"""

import logging
from typing import Dict, Any, List, Optional
import boto3
from botocore.exceptions import ClientError
import time

logger = logging.getLogger(__name__)


class ALBManager:
    """Manages AWS Application Load Balancers."""
    
    def __init__(self, elb_client, ec2_client):
        """
        Initialize ALBManager.
        
        Args:
            elb_client: Boto3 ELBv2 client
            ec2_client: Boto3 EC2 client
        """
        self.elb_client = elb_client
        self.ec2_client = ec2_client
    
    def get_all_subnets(self, vpc_id: Optional[str] = None) -> List[str]:
        """
        Get all subnets in the VPC (across all availability zones).
        
        Args:
            vpc_id: VPC ID (uses default if not specified)
            
        Returns:
            list: List of subnet IDs
        """
        try:
            if not vpc_id:
                vpc_id = self._get_default_vpc()
            
            response = self.ec2_client.describe_subnets(
                Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
            )
            
            subnet_ids = [subnet["SubnetId"] for subnet in response["Subnets"]]
            
            # Ensure we have subnets from at least 2 AZs (required for ALB)
            if len(subnet_ids) < 2:
                raise Exception("ALB requires subnets in at least 2 availability zones")
            
            logger.info(f"Found {len(subnet_ids)} subnets in VPC {vpc_id}")
            return subnet_ids
            
        except ClientError as e:
            logger.error(f"Failed to get subnets: {e}")
            raise
    
    def create_target_group(
        self,
        name: str,
        vpc_id: str,
        port: int = 80,
        protocol: str = "HTTP",
        tags: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Create a target group for the ALB.
        
        Args:
            name: Target group name
            vpc_id: VPC ID
            port: Target port
            protocol: Target protocol
            tags: Optional tags
            
        Returns:
            dict: Target group information
        """
        try:
            params = {
                "Name": name,
                "Protocol": protocol,
                "Port": port,
                "VpcId": vpc_id,
                "HealthCheckProtocol": protocol,
                "HealthCheckPath": "/",
                "HealthCheckIntervalSeconds": 30,
                "HealthCheckTimeoutSeconds": 5,
                "HealthyThresholdCount": 2,
                "UnhealthyThresholdCount": 2,
                "TargetType": "instance"
            }
            
            if tags:
                params["Tags"] = tags
            
            response = self.elb_client.create_target_group(**params)
            target_group = response["TargetGroups"][0]
            
            logger.info(f"Created target group: {name} ({target_group['TargetGroupArn']})")
            
            return {
                "TargetGroupArn": target_group["TargetGroupArn"],
                "TargetGroupName": name
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'DuplicateTargetGroupName':
                logger.warning(f"Target group '{name}' already exists")
                # Get existing target group
                response = self.elb_client.describe_target_groups(Names=[name])
                target_group = response["TargetGroups"][0]
                return {
                    "TargetGroupArn": target_group["TargetGroupArn"],
                    "TargetGroupName": name,
                    "Exists": True
                }
            logger.error(f"Failed to create target group: {e}")
            raise
    
    def register_targets(
        self,
        target_group_arn: str,
        instance_ids: List[str]
    ) -> bool:
        """
        Register instances to a target group.
        
        Args:
            target_group_arn: Target group ARN
            instance_ids: List of instance IDs to register
            
        Returns:
            bool: True if successful
        """
        try:
            targets = [{"Id": instance_id} for instance_id in instance_ids]
            
            self.elb_client.register_targets(
                TargetGroupArn=target_group_arn,
                Targets=targets
            )
            
            logger.info(f"Registered {len(instance_ids)} instances to target group")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to register targets: {e}")
            return False
    
    def create_load_balancer(
        self,
        name: str,
        security_groups: List[str],
        subnets: List[str],
        tags: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Create an Application Load Balancer.
        
        Args:
            name: Load balancer name
            security_groups: List of security group IDs
            subnets: List of subnet IDs (at least 2 in different AZs)
            tags: Optional tags
            
        Returns:
            dict: Load balancer information
        """
        try:
            params = {
                "Name": name,
                "Subnets": subnets,
                "SecurityGroups": security_groups,
                "Scheme": "internet-facing",
                "Type": "application",
                "IpAddressType": "ipv4"
            }
            
            if tags:
                params["Tags"] = tags
            
            response = self.elb_client.create_load_balancer(**params)
            load_balancer = response["LoadBalancers"][0]
            
            logger.info(f"Created load balancer: {name} ({load_balancer['LoadBalancerArn']})")
            
            # Wait for load balancer to be active
            logger.info("Waiting for load balancer to be active...")
            waiter = self.elb_client.get_waiter('load_balancer_available')
            waiter.wait(LoadBalancerArns=[load_balancer['LoadBalancerArn']])
            
            logger.info("Load balancer is now active")
            
            return {
                "LoadBalancerArn": load_balancer["LoadBalancerArn"],
                "LoadBalancerName": name,
                "DNSName": load_balancer["DNSName"],
                "Scheme": load_balancer["Scheme"]
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'DuplicateLoadBalancer':
                logger.warning(f"Load balancer '{name}' already exists")
                # Get existing load balancer
                response = self.elb_client.describe_load_balancers(Names=[name])
                lb = response["LoadBalancers"][0]
                return {
                    "LoadBalancerArn": lb["LoadBalancerArn"],
                    "LoadBalancerName": name,
                    "DNSName": lb["DNSName"],
                    "Scheme": lb["Scheme"],
                    "Exists": True
                }
            logger.error(f"Failed to create load balancer: {e}")
            raise
    
    def create_listener(
        self,
        load_balancer_arn: str,
        target_group_arn: str,
        port: int = 80,
        protocol: str = "HTTP"
    ) -> Dict[str, Any]:
        """
        Create a listener for the load balancer.
        
        Args:
            load_balancer_arn: Load balancer ARN
            target_group_arn: Target group ARN
            port: Listener port
            protocol: Listener protocol
            
        Returns:
            dict: Listener information
        """
        try:
            response = self.elb_client.create_listener(
                LoadBalancerArn=load_balancer_arn,
                Protocol=protocol,
                Port=port,
                DefaultActions=[{
                    "Type": "forward",
                    "TargetGroupArn": target_group_arn
                }]
            )
            
            listener = response["Listeners"][0]
            logger.info(f"Created listener on port {port}")
            
            return {
                "ListenerArn": listener["ListenerArn"],
                "Port": port,
                "Protocol": protocol
            }
            
        except ClientError as e:
            logger.error(f"Failed to create listener: {e}")
            raise
    
    def delete_load_balancer(self, load_balancer_arn: str) -> bool:
        """
        Delete a load balancer.
        
        Args:
            load_balancer_arn: Load balancer ARN
            
        Returns:
            bool: True if successful
        """
        try:
            self.elb_client.delete_load_balancer(LoadBalancerArn=load_balancer_arn)
            logger.info(f"Deleted load balancer: {load_balancer_arn}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete load balancer: {e}")
            return False
    
    def delete_target_group(self, target_group_arn: str) -> bool:
        """
        Delete a target group.
        
        Args:
            target_group_arn: Target group ARN
            
        Returns:
            bool: True if successful
        """
        try:
            self.elb_client.delete_target_group(TargetGroupArn=target_group_arn)
            logger.info(f"Deleted target group: {target_group_arn}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete target group: {e}")
            return False
    
    def _get_default_vpc(self) -> str:
        """Get the default VPC ID."""
        try:
            response = self.ec2_client.describe_vpcs(
                Filters=[{"Name": "isDefault", "Values": ["true"]}]
            )
            if response["Vpcs"]:
                return response["Vpcs"][0]["VpcId"]
            raise Exception("No default VPC found")
        except ClientError as e:
            logger.error(f"Failed to get default VPC: {e}")
            raise
