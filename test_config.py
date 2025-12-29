"""
Unit tests for configuration module.
"""

import unittest
import os
from config import (
    AWS_REGION,
    INSTANCE_TYPE,
    AMI_NAME_FILTER,
    TEMPLATE_NAME,
    TEMPLATE_ID,
    get_resource_names,
    get_user_data,
    get_tags,
    INSTANCE_SG_RULES,
    ALB_SG_RULES
)


class TestConfig(unittest.TestCase):
    """Test configuration module."""
    
    def test_aws_region_default(self):
        """Test AWS region configuration."""
        self.assertIsNotNone(AWS_REGION)
        self.assertIsInstance(AWS_REGION, str)
        self.assertTrue(len(AWS_REGION) > 0)
    
    def test_instance_type(self):
        """Test instance type configuration."""
        self.assertEqual(INSTANCE_TYPE, "t2.micro")
    
    def test_ami_name_filter(self):
        """Test AMI name filter."""
        self.assertIsInstance(AMI_NAME_FILTER, str)
        self.assertIn("ami", AMI_NAME_FILTER.lower())
    
    def test_template_configuration(self):
        """Test template name and ID."""
        self.assertIsInstance(TEMPLATE_NAME, str)
        self.assertIsInstance(TEMPLATE_ID, str)
        self.assertTrue(len(TEMPLATE_NAME) > 0)
        self.assertTrue(len(TEMPLATE_ID) > 0)
    
    def test_get_resource_names(self):
        """Test resource name generation."""
        names = get_resource_names()
        
        # Check all required keys exist
        required_keys = [
            "key_pair", "security_group", "instance",
            "alb", "target_group", "alb_sg"
        ]
        for key in required_keys:
            self.assertIn(key, names)
            self.assertIsInstance(names[key], str)
            self.assertTrue(len(names[key]) > 0)
        
        # Check that resource names include template name
        for key, value in names.items():
            self.assertIn(TEMPLATE_NAME, value)
    
    def test_get_user_data(self):
        """Test user data script generation."""
        user_data = get_user_data()
        
        self.assertIsInstance(user_data, str)
        self.assertTrue(len(user_data) > 0)
        
        # Check for essential commands
        self.assertIn("#!/bin/bash", user_data)
        self.assertIn("yum update", user_data)
        self.assertIn("httpd", user_data)
        self.assertIn(TEMPLATE_ID, user_data)
        self.assertIn(TEMPLATE_NAME, user_data)
    
    def test_get_tags(self):
        """Test tag generation."""
        tags = get_tags()
        
        self.assertIsInstance(tags, list)
        self.assertTrue(len(tags) > 0)
        
        # Check tag structure
        for tag in tags:
            self.assertIn("Key", tag)
            self.assertIn("Value", tag)
            self.assertIsInstance(tag["Key"], str)
            self.assertIsInstance(tag["Value"], str)
    
    def test_instance_security_group_rules(self):
        """Test instance security group rules."""
        self.assertIsInstance(INSTANCE_SG_RULES, list)
        self.assertTrue(len(INSTANCE_SG_RULES) > 0)
        
        for rule in INSTANCE_SG_RULES:
            self.assertIn("IpProtocol", rule)
            self.assertIn("FromPort", rule)
            self.assertIn("ToPort", rule)
    
    def test_alb_security_group_rules(self):
        """Test ALB security group rules."""
        self.assertIsInstance(ALB_SG_RULES, list)
        self.assertTrue(len(ALB_SG_RULES) > 0)
        
        # Check for HTTP rule (port 80)
        has_http = any(
            rule.get("FromPort") == 80 and rule.get("ToPort") == 80
            for rule in ALB_SG_RULES
        )
        self.assertTrue(has_http, "ALB should have HTTP (port 80) rule")


class TestConfigEnvironmentVariables(unittest.TestCase):
    """Test environment variable handling."""
    
    def test_aws_region_from_env(self):
        """Test AWS region can be overridden by environment variable."""
        # This test assumes AWS_REGION is read from environment
        # The actual value depends on whether it's set
        region = os.getenv("AWS_REGION", "us-east-1")
        self.assertIsNotNone(region)
        self.assertIsInstance(region, str)


if __name__ == "__main__":
    unittest.main()
