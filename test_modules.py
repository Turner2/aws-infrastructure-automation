"""
Unit tests for AWS modules.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from botocore.exceptions import ClientError

from modules import (
    KeyPairManager,
    SecurityGroupManager,
    EC2InstanceManager,
    ALBManager
)


class TestKeyPairManager(unittest.TestCase):
    """Test KeyPairManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_ec2_client = Mock()
        self.key_pair_name = "test-keypair"
        self.manager = KeyPairManager(self.mock_ec2_client)
    
    def test_initialization(self):
        """Test KeyPairManager initialization."""
        self.assertEqual(self.manager.ec2_client, self.mock_ec2_client)
    
    def test_create_key_pair_success(self):
        """Test successful key pair creation."""
        self.mock_ec2_client.describe_key_pairs.side_effect = ClientError(
            {'Error': {'Code': 'InvalidKeyPair.NotFound'}},
            'DescribeKeyPairs'
        )
        self.mock_ec2_client.create_key_pair.return_value = {
            'KeyMaterial': 'test-key-material',
            'KeyName': self.key_pair_name,
            'KeyPairId': 'key-12345'
        }
        
        result = self.manager.create_key_pair(self.key_pair_name)
        
        self.assertIsInstance(result, dict)
        self.assertIn('KeyName', result)
        self.assertEqual(result['KeyName'], self.key_pair_name)
    
    def test_delete_key_pair_success(self):
        """Test successful key pair deletion."""
        self.mock_ec2_client.delete_key_pair.return_value = {}
        
        result = self.manager.delete_key_pair(self.key_pair_name)
        
        self.assertTrue(result)
        self.mock_ec2_client.delete_key_pair.assert_called_once()


class TestSecurityGroupManager(unittest.TestCase):
    """Test SecurityGroupManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_ec2_client = Mock()
        self.mock_ec2_resource = Mock()
        self.group_name = "test-sg"
        self.description = "Test security group"
        self.manager = SecurityGroupManager(
            self.mock_ec2_client,
            self.mock_ec2_resource
        )
    
    def test_initialization(self):
        """Test SecurityGroupManager initialization."""
        self.assertEqual(self.manager.ec2_client, self.mock_ec2_client)
        self.assertEqual(self.manager.ec2_resource, self.mock_ec2_resource)
    
    def test_create_security_group_success(self):
        """Test successful security group creation."""
        vpc_id = "vpc-12345"
        self.mock_ec2_client.describe_security_groups.side_effect = ClientError(
            {'Error': {'Code': 'InvalidGroup.NotFound'}},
            'DescribeSecurityGroups'
        )
        self.mock_ec2_client.describe_vpcs.return_value = {
            'Vpcs': [{'VpcId': vpc_id}]
        }
        self.mock_ec2_client.create_security_group.return_value = {
            'GroupId': 'sg-12345'
        }
        
        result = self.manager.create_security_group(
            self.group_name,
            self.description
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('GroupId', result)
    
    def test_add_ingress_rules_success(self):
        """Test adding ingress rules."""
        rules = [
            {
                'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'CidrIp': '0.0.0.0/0'
            }
        ]
        
        result = self.manager.add_ingress_rules('sg-12345', rules)
        
        self.assertTrue(result)
        self.mock_ec2_client.authorize_security_group_ingress.assert_called_once()
    
    def test_delete_security_group_success(self):
        """Test successful security group deletion."""
        self.mock_ec2_client.delete_security_group.return_value = {}
        
        result = self.manager.delete_security_group('sg-12345')
        
        self.assertTrue(result)
        self.mock_ec2_client.delete_security_group.assert_called_once()


class TestEC2InstanceManager(unittest.TestCase):
    """Test EC2InstanceManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_ec2_client = Mock()
        self.mock_ec2_resource = Mock()
        self.manager = EC2InstanceManager(
            self.mock_ec2_client,
            self.mock_ec2_resource
        )
    
    def test_initialization(self):
        """Test EC2InstanceManager initialization."""
        self.assertEqual(self.manager.ec2_client, self.mock_ec2_client)
        self.assertEqual(self.manager.ec2_resource, self.mock_ec2_resource)
    
    def test_get_ami_id_success(self):
        """Test getting AMI ID."""
        self.mock_ec2_client.describe_images.return_value = {
            'Images': [
                {'ImageId': 'ami-12345', 'CreationDate': '2024-01-01T00:00:00.000Z', 'Name': 'test-ami-1'},
                {'ImageId': 'ami-67890', 'CreationDate': '2024-01-02T00:00:00.000Z', 'Name': 'test-ami-2'}
            ]
        }
        
        ami_id = self.manager.get_ami_id('test-filter')
        
        self.assertEqual(ami_id, 'ami-67890')
    
    def test_create_instance_success(self):
        """Test successful instance creation."""
        # Mock the run_instances response
        self.mock_ec2_client.run_instances.return_value = {
            'Instances': [{
                'InstanceId': 'i-12345',
                'State': {'Name': 'pending'},
                'PublicDnsName': '',
                'PublicIpAddress': ''
            }]
        }
        
        # Mock the describe_instances response for get_instance_info
        self.mock_ec2_client.describe_instances.return_value = {
            'Reservations': [{
                'Instances': [{
                    'InstanceId': 'i-12345',
                    'State': {'Name': 'running'},
                    'PublicDnsName': 'ec2-test.amazonaws.com',
                    'PublicIpAddress': '1.2.3.4',
                    'PrivateIpAddress': '10.0.0.1',
                    'InstanceType': 't2.micro',
                    'Placement': {'AvailabilityZone': 'us-east-1a'}
                }]
            }]
        }
        
        result = self.manager.create_instance(
            ami_id='ami-12345',
            instance_type='t2.micro',
            key_name='test-key',
            security_group_ids=['sg-12345'],
            user_data='#!/bin/bash\necho "test"',
            instance_name='test-instance',
            tags=[]
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('InstanceId', result)
    
    def test_terminate_instance_success(self):
        """Test successful instance termination."""
        self.mock_ec2_client.terminate_instances.return_value = {}
        
        result = self.manager.terminate_instance('i-12345')
        
        self.assertTrue(result)
        self.mock_ec2_client.terminate_instances.assert_called_once()


class TestALBManager(unittest.TestCase):
    """Test ALBManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_elb_client = Mock()
        self.mock_ec2_client = Mock()
        self.alb_name = "test-alb"
        self.manager = ALBManager(
            self.mock_elb_client,
            self.mock_ec2_client
        )
    
    def test_initialization(self):
        """Test ALBManager initialization."""
        self.assertEqual(self.manager.elb_client, self.mock_elb_client)
        self.assertEqual(self.manager.ec2_client, self.mock_ec2_client)
    
    def test_get_all_subnets_success(self):
        """Test getting subnets."""
        self.mock_ec2_client.describe_vpcs.return_value = {
            'Vpcs': [{'VpcId': 'vpc-12345', 'IsDefault': True}]
        }
        self.mock_ec2_client.describe_subnets.return_value = {
            'Subnets': [
                {'SubnetId': 'subnet-1', 'AvailabilityZone': 'us-east-1a'},
                {'SubnetId': 'subnet-2', 'AvailabilityZone': 'us-east-1b'}
            ]
        }
        
        subnet_ids = self.manager.get_all_subnets('vpc-12345')
        
        self.assertEqual(len(subnet_ids), 2)
        self.assertIn('subnet-1', subnet_ids)
        self.assertIn('subnet-2', subnet_ids)
    
    def test_create_target_group_success(self):
        """Test successful target group creation."""
        self.mock_elb_client.describe_target_groups.side_effect = ClientError(
            {'Error': {'Code': 'TargetGroupNotFound'}},
            'DescribeTargetGroups'
        )
        self.mock_elb_client.create_target_group.return_value = {
            'TargetGroups': [{'TargetGroupArn': 'arn:aws:elasticloadbalancing:...'}]
        }
        
        result = self.manager.create_target_group('test-tg', 'vpc-12345')
        
        self.assertIsInstance(result, dict)
        self.assertIn('TargetGroupArn', result)
    
    def test_create_load_balancer_success(self):
        """Test successful load balancer creation."""
        self.mock_elb_client.describe_load_balancers.side_effect = ClientError(
            {'Error': {'Code': 'LoadBalancerNotFound'}},
            'DescribeLoadBalancers'
        )
        self.mock_elb_client.create_load_balancer.return_value = {
            'LoadBalancers': [{
                'LoadBalancerArn': 'arn:aws:elasticloadbalancing:...',
                'DNSName': 'test-alb-123456.us-east-1.elb.amazonaws.com',
                'LoadBalancerName': 'test-alb',
                'Scheme': 'internet-facing',
                'VpcId': 'vpc-12345',
                'State': {'Code': 'active'},
                'Type': 'application'
            }]
        }
        
        result = self.manager.create_load_balancer(
            self.alb_name,
            ['subnet-1', 'subnet-2'],
            ['sg-12345']
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('LoadBalancerArn', result)


if __name__ == "__main__":
    unittest.main()
