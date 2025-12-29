"""
AWS EC2 Key Pair management module.
"""

import logging
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class KeyPairManager:
    """Manages AWS EC2 Key Pairs."""
    
    def __init__(self, ec2_client):
        """
        Initialize KeyPairManager.
        
        Args:
            ec2_client: Boto3 EC2 client
        """
        self.ec2_client = ec2_client
    
    def create_key_pair(self, key_name: str, save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new EC2 key pair.
        
        Args:
            key_name: Name for the key pair
            save_path: Optional path to save the private key file
            
        Returns:
            dict: Key pair information including KeyPairId and KeyName
            
        Raises:
            ClientError: If key pair creation fails
        """
        try:
            # Check if key pair already exists
            try:
                response = self.ec2_client.describe_key_pairs(KeyNames=[key_name])
                logger.info(f"Key pair '{key_name}' already exists")
                return {
                    "KeyPairId": response["KeyPairs"][0]["KeyPairId"],
                    "KeyName": key_name,
                    "Exists": True
                }
            except ClientError as e:
                if e.response['Error']['Code'] != 'InvalidKeyPair.NotFound':
                    raise
            
            # Create new key pair
            response = self.ec2_client.create_key_pair(KeyName=key_name)
            logger.info(f"Created key pair: {key_name}")
            
            # Save private key if path provided
            if save_path:
                with open(save_path, 'w') as f:
                    f.write(response['KeyMaterial'])
                import os
                os.chmod(save_path, 0o400)
                logger.info(f"Saved private key to: {save_path}")
            
            return {
                "KeyPairId": response["KeyPairId"],
                "KeyName": key_name,
                "KeyMaterial": response.get("KeyMaterial"),
                "Exists": False
            }
            
        except ClientError as e:
            logger.error(f"Failed to create key pair: {e}")
            raise
    
    def delete_key_pair(self, key_name: str) -> bool:
        """
        Delete an EC2 key pair.
        
        Args:
            key_name: Name of the key pair to delete
            
        Returns:
            bool: True if successful
        """
        try:
            self.ec2_client.delete_key_pair(KeyName=key_name)
            logger.info(f"Deleted key pair: {key_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete key pair: {e}")
            return False
    
    def key_pair_exists(self, key_name: str) -> bool:
        """
        Check if a key pair exists.
        
        Args:
            key_name: Name of the key pair
            
        Returns:
            bool: True if exists, False otherwise
        """
        try:
            self.ec2_client.describe_key_pairs(KeyNames=[key_name])
            return True
        except ClientError:
            return False
