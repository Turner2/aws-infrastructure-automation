# Testing Documentation

## Overview

This document provides comprehensive information about the testing infrastructure for the AWS Infrastructure Automation project.

## Test Structure

The test suite is organized into four main test files:

### 1. **test_config.py** - Configuration Tests

Tests the configuration module to ensure all settings are properly defined and formatted.

**Test Classes:**

- `TestConfig`: Tests core configuration values
- `TestConfigEnvironmentVariables`: Tests environment variable handling

**Coverage:**

- AWS region configuration
- Instance type settings
- AMI filters
- Resource name generation
- User data script generation
- Tag structure
- Security group rules (EC2 and ALB)

### 2. **test_modules.py** - Module Unit Tests

Tests individual AWS service manager classes with mocked AWS SDK calls.

**Test Classes:**

- `TestKeyPairManager`: EC2 key pair operations
- `TestSecurityGroupManager`: Security group operations
- `TestEC2InstanceManager`: EC2 instance management
- `TestALBManager`: Application Load Balancer operations

**Coverage:**

- Manager initialization
- Resource creation and deletion
- Error handling
- AWS API interaction patterns

### 3. **test_utils.py** - Utility Function Tests

Tests helper functions and utility modules.

**Test Classes:**

- `TestUtilityFunctions`: Core utility functions
- `TestUtilityInputValidation`: Input validation and edge cases

**Coverage:**

- Public IP retrieval
- Formatted output functions
- Progress indicators
- Error handling

### 4. **test_integration.py** - Integration Tests

Tests component interactions and deployment workflows.

**Test Classes:**

- `TestDeploymentWorkflow`: Complete deployment scenarios
- `TestResourceNameConsistency`: Resource naming validation
- `TestConfigurationIntegration`: Config integration with modules
- `TestErrorHandling`: End-to-end error scenarios

**Coverage:**

- Multi-component workflows
- Resource naming consistency
- Configuration validation
- Error propagation

## Running Tests

### Using unittest (Standard Library)

Run all tests:

```bash
python run_tests.py
```

Run specific test file:

```bash
python -m unittest test_config.py
```

Run specific test class:

```bash
python -m unittest test_config.TestConfig
```

Run specific test method:

```bash
python -m unittest test_config.TestConfig.test_aws_region_default
```

### Using pytest (Recommended)

Run all tests with verbose output:

```bash
pytest test_*.py -v
```

Run with coverage report:

```bash
pytest test_*.py -v --cov=. --cov-report=term-missing --cov-report=html
```

Run specific test file:

```bash
pytest test_config.py -v
```

Run specific test:

```bash
pytest test_config.py::TestConfig::test_aws_region_default -v
```

Run tests matching a pattern:

```bash
pytest -k "test_create" -v
```

## Test Coverage

Current test coverage metrics:

| Module                    | Coverage | Status       |
| ------------------------- | -------- | ------------ |
| config.py                 | 100%     | ✅ Excellent |
| modules/**init**.py       | 100%     | ✅ Excellent |
| utils/**init**.py         | 100%     | ✅ Excellent |
| utils/helpers.py          | 97%      | ✅ Excellent |
| modules/ec2_instance.py   | 65%      | ⚠️ Good      |
| modules/security_group.py | 64%      | ⚠️ Good      |
| modules/keypair.py        | 56%      | ⚠️ Good      |
| modules/alb.py            | 41%      | ⚠️ Fair      |

**Overall Coverage: 56%** (of testable code)

**Note:** `deploy.py` and `cleanup.py` are main scripts with 0% coverage as they require AWS credentials and are tested manually or through integration tests.

### Viewing Coverage Report

After running pytest with coverage, open the HTML report:

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Test Dependencies

Required packages (from requirements.txt):

- `boto3>=1.42.0` - AWS SDK for Python
- `botocore>=1.42.0` - Low-level AWS SDK core
- `requests>=2.32.0` - HTTP library
- `pytest>=7.4.0` - Testing framework
- `pytest-cov>=4.1.0` - Coverage plugin for pytest
- `pytest-mock>=3.12.0` - Mock fixtures for pytest
- `coverage>=7.3.0` - Code coverage measurement

## Test Patterns and Best Practices

### 1. Mocking AWS Services

```python
from unittest.mock import Mock
import boto3

# Create mock clients
mock_ec2_client = Mock()
mock_ec2_client.describe_instances.return_value = {
    'Reservations': [{'Instances': [...]}]
}
```

### 2. Testing Exceptions

```python
from botocore.exceptions import ClientError

mock_client.create_key_pair.side_effect = ClientError(
    {'Error': {'Code': 'InvalidKeyPair.Duplicate'}},
    'CreateKeyPair'
)
```

### 3. Testing Configuration

```python
def test_resource_names():
    names = get_resource_names()
    assert all(isinstance(v, str) for v in names.values())
```

## Continuous Integration

Tests are automatically run on:

- Every push to main branch
- Every pull request
- Manual workflow dispatch

See `.github/workflows/` for CI configuration.

## Writing New Tests

### Guidelines

1. **Follow naming conventions:**

   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test methods: `test_*`

2. **Use descriptive names:**

   ```python
   def test_create_key_pair_with_valid_name_succeeds(self):
       # Test implementation
   ```

3. **Mock external dependencies:**

   - Always mock AWS API calls
   - Mock network requests
   - Mock file system operations

4. **Test edge cases:**

   - Empty inputs
   - None values
   - Invalid data types
   - Error conditions

5. **Keep tests independent:**
   - Each test should be able to run in isolation
   - Use `setUp()` and `tearDown()` for test fixtures
   - Don't depend on execution order

### Example Test Template

```python
import unittest
from unittest.mock import Mock, patch

class TestNewFeature(unittest.TestCase):
    """Test new feature functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        # Setup code

    def test_feature_with_valid_input(self):
        """Test feature with valid input."""
        # Arrange
        expected_result = "expected"

        # Act
        result = function_under_test()

        # Assert
        self.assertEqual(result, expected_result)

    def test_feature_with_invalid_input(self):
        """Test feature handles invalid input."""
        with self.assertRaises(ValueError):
            function_under_test(invalid_input)

    def tearDown(self):
        """Clean up after tests."""
        # Cleanup code
```

## Troubleshooting

### Common Issues

**Issue:** Tests fail with "Module not found"

```bash
# Solution: Ensure you're running from project root
cd /path/to/aws-infrastructure-automation
python run_tests.py
```

**Issue:** Import errors in tests

```bash
# Solution: Install test dependencies
pip install -r requirements.txt
```

**Issue:** Mocking not working as expected

```python
# Problem: Wrong import path
@patch('requests.get')  # ❌ Wrong

# Solution: Patch where it's used
@patch('utils.helpers.requests.get')  # ✅ Correct
```

## Test Results

### Latest Test Run

```
Ran 45 tests in 0.005s

OK

Test Results:
- ✅ Configuration Tests: 10/10 passed
- ✅ Module Tests: 17/17 passed
- ✅ Integration Tests: 10/10 passed
- ✅ Utility Tests: 8/8 passed

Total: 45/45 tests passed (100%)
```

## Future Improvements

1. **Increase Coverage:**

   - Add tests for error handling paths
   - Test more edge cases in modules
   - Add integration tests for complete workflows

2. **Performance Tests:**

   - Add benchmarks for resource creation
   - Test with large numbers of resources

3. **End-to-End Tests:**

   - Test with actual AWS sandbox environment
   - Automated deployment and cleanup tests

4. **Documentation:**
   - Add more inline test documentation
   - Create video tutorials for writing tests

## Contributing

When contributing new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Update this documentation
5. Add test examples for new patterns

## Support

For questions about testing:

- Check existing test files for examples
- Review this documentation
- Open an issue on GitHub
- Contact maintainers

---

**Last Updated:** December 29, 2025  
**Test Suite Version:** 1.0  
**Python Version:** 3.8+
