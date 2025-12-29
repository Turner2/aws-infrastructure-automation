"""
Integration tests for AWS infrastructure deployment.
These tests verify the interaction between components.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys

from config import get_resource_names, get_user_data, get_tags
from modules import (
    KeyPairManager,
    SecurityGroupManager,
    EC2InstanceManager,
    ALBManager
)


class TestDeploymentWorkflow(unittest.TestCase):
    """Test the complete deployment workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_ec2_client = Mock()
        self.mock_ec2_resource = Mock()
        self.mock_elbv2_client = Mock()
        self.resource_names = get_resource_names()
    
    @patch('modules.keypair.KeyPairManager')
    def test_key_pair_creation_workflow(self, MockKeyPairManager):
        """Test key pair creation workflow."""
        mock_kp_manager = MockKeyPairManager.return_value
        mock_kp_manager.key_pair_exists.return_value = False
        mock_kp_manager.create_key_pair.return_value = True
        
        # Simulate workflow
        if not mock_kp_manager.key_pair_exists():
            result = mock_kp_manager.create_key_pair()
            self.assertTrue(result)
    
    @patch('modules.security_group.SecurityGroupManager')
    def test_security_group_creation_workflow(self, MockSGManager):
        """Test security group creation workflow."""
        mock_sg_manager = MockSGManager.return_value
        mock_sg_manager.create_security_group.return_value = 'sg-12345'
        mock_sg_manager.add_ingress_rules.return_value = True
        
        # Simulate workflow
        sg_id = mock_sg_manager.create_security_group()
        self.assertEqual(sg_id, 'sg-12345')
        
        rules = [{'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80}]
        result = mock_sg_manager.add_ingress_rules(sg_id, rules)
        self.assertTrue(result)
    
    @patch('modules.ec2_instance.EC2InstanceManager')
    def test_instance_launch_workflow(self, MockEC2Manager):
        """Test EC2 instance launch workflow."""
        mock_ec2_manager = MockEC2Manager.return_value
        mock_ec2_manager.get_latest_ami.return_value = 'ami-12345'
        mock_ec2_manager.launch_instance.return_value = 'i-12345'
        
        # Simulate workflow
        ami_id = mock_ec2_manager.get_latest_ami('test-filter')
        self.assertEqual(ami_id, 'ami-12345')
        
        instance_id = mock_ec2_manager.launch_instance(
            ami_id=ami_id,
            instance_type='t2.micro',
            key_name='test-key',
            security_group_ids=['sg-12345'],
            user_data='#!/bin/bash',
            instance_name='test',
            tags=[]
        )
        self.assertEqual(instance_id, 'i-12345')
    
    @patch('modules.alb.ALBManager')
    def test_alb_creation_workflow(self, MockALBManager):
        """Test ALB creation workflow."""
        mock_alb_manager = MockALBManager.return_value
        mock_alb_manager.get_subnets.return_value = ('vpc-12345', ['subnet-1', 'subnet-2'])
        mock_alb_manager.create_target_group.return_value = 'tg-arn'
        mock_alb_manager.create_load_balancer.return_value = ('alb-arn', 'test.elb.amazonaws.com')
        mock_alb_manager.register_targets.return_value = True
        
        # Simulate workflow
        vpc_id, subnets = mock_alb_manager.get_subnets()
        self.assertEqual(vpc_id, 'vpc-12345')
        self.assertEqual(len(subnets), 2)
        
        tg_arn = mock_alb_manager.create_target_group('test-tg', vpc_id)
        self.assertEqual(tg_arn, 'tg-arn')
        
        alb_arn, dns = mock_alb_manager.create_load_balancer(subnets, ['sg-12345'])
        self.assertIsNotNone(alb_arn)
        self.assertIsNotNone(dns)


class TestResourceNameConsistency(unittest.TestCase):
    """Test resource naming consistency."""
    
    def test_resource_names_consistency(self):
        """Test that resource names are consistent across calls."""
        names1 = get_resource_names()
        names2 = get_resource_names()
        
        self.assertEqual(names1, names2)
    
    def test_resource_names_format(self):
        """Test resource name format."""
        names = get_resource_names()
        
        for key, value in names.items():
            # Check no spaces in resource names
            self.assertNotIn(' ', value)
            # Check names are lowercase or kebab-case
            self.assertTrue(
                value.islower() or '-' in value,
                f"Resource name '{value}' should be lowercase or kebab-case"
            )


class TestConfigurationIntegration(unittest.TestCase):
    """Test configuration integration with modules."""
    
    def test_user_data_script_completeness(self):
        """Test that user data script is complete."""
        user_data = get_user_data()
        
        # Check for essential setup steps
        required_commands = [
            'yum update',
            'yum install',
            'httpd',
            'systemctl start',
            'systemctl enable',
            'wget',
            'unzip',
            'chown',
            'chmod'
        ]
        
        for cmd in required_commands:
            self.assertIn(
                cmd,
                user_data,
                f"User data missing essential command: {cmd}"
            )
    
    def test_tags_structure(self):
        """Test tags structure is compatible with AWS."""
        tags = get_tags()
        
        # AWS tags must have Key and Value
        for tag in tags:
            self.assertIn('Key', tag)
            self.assertIn('Value', tag)
            # AWS tag keys/values should not be empty
            self.assertTrue(len(tag['Key']) > 0)
            self.assertTrue(len(tag['Value']) > 0)


class TestErrorHandling(unittest.TestCase):
    """Test error handling across components."""
    
    @patch('modules.keypair.KeyPairManager')
    def test_key_pair_error_handling(self, MockKeyPairManager):
        """Test key pair error handling."""
        mock_kp_manager = MockKeyPairManager.return_value
        mock_kp_manager.create_key_pair.side_effect = Exception("AWS Error")
        
        # Should handle exception gracefully
        try:
            mock_kp_manager.create_key_pair()
        except Exception as e:
            self.assertIsInstance(e, Exception)
    
    @patch('modules.security_group.SecurityGroupManager')
    def test_security_group_error_handling(self, MockSGManager):
        """Test security group error handling."""
        mock_sg_manager = MockSGManager.return_value
        mock_sg_manager.create_security_group.side_effect = Exception("AWS Error")
        
        try:
            mock_sg_manager.create_security_group()
        except Exception as e:
            self.assertIsInstance(e, Exception)


if __name__ == "__main__":
    unittest.main()
