# Contributing to AWS Infrastructure Automation

First off, thank you for considering contributing to this project! 🎉

## 🤝 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected behavior**
- **Actual behavior**
- **AWS region** you're using
- **Python version** (`python --version`)
- **Boto3 version** (`pip show boto3`)
- **Error messages** or logs

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **Clear title and description**
- **Use case** - why is this enhancement useful?
- **Possible implementation** - how might this work?
- **Alternatives** - what other solutions have you considered?

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/aws-boto3-automation.git
   cd aws-boto3-automation
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Follow the coding style (see below)
   - Add/update documentation
   - Add tests if applicable

4. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**

## 📝 Coding Standards

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these specifics:

```python
# Use 4 spaces for indentation (no tabs)
def my_function():
    pass

# Maximum line length: 100 characters
# (slightly relaxed from PEP 8's 79)

# Use double quotes for strings
message = "Hello, world!"

# Type hints for function signatures
def create_instance(
    ami_id: str,
    instance_type: str
) -> Dict[str, Any]:
    pass

# Docstrings for all public functions/classes
def my_function(param: str) -> bool:
    """
    Brief description of function.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
    """
    pass
```

### Module Structure

```python
"""
Module docstring describing purpose.
"""

# Standard library imports
import os
import sys

# Third-party imports
import boto3
from botocore.exceptions import ClientError

# Local imports
from config import AWS_REGION
from utils import print_section

# Constants
DEFAULT_TIMEOUT = 30

# Classes and functions
class MyClass:
    """Class docstring."""
    pass
```

### Error Handling

Always handle specific exceptions:

```python
# Good
try:
    response = client.create_instance(...)
except ClientError as e:
    if e.response['Error']['Code'] == 'InstanceLimitExceeded':
        logger.error("Instance limit reached")
        # Handle specifically
    else:
        raise

# Avoid
try:
    response = client.create_instance(...)
except Exception:
    pass  # Never do this!
```

### Logging

Use structured logging:

```python
import logging

logger = logging.getLogger(__name__)

# Good logging practices
logger.info(f"Creating instance with AMI {ami_id}")
logger.warning(f"Resource already exists: {resource_id}")
logger.error(f"Failed to create resource: {e}")
logger.exception("Unexpected error occurred")  # Includes traceback
```

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-mock moto

# Run tests
pytest tests/

# Run with coverage
pytest --cov=modules --cov=utils tests/
```

### Writing Tests

```python
import pytest
from moto import mock_ec2
from modules.keypair import KeyPairManager

@mock_ec2
def test_create_key_pair():
    """Test key pair creation."""
    import boto3
    
    client = boto3.client('ec2', region_name='us-east-1')
    manager = KeyPairManager(client)
    
    result = manager.create_key_pair('test-key')
    
    assert result['KeyName'] == 'test-key'
    assert 'KeyPairId' in result
```

## 📚 Documentation

### Code Comments

```python
# Use comments to explain WHY, not WHAT
# Good:
# Wait for dependencies to clear before retry
time.sleep(10)

# Bad:
# Sleep for 10 seconds
time.sleep(10)
```

### Docstrings

```python
def create_security_group(
    self,
    group_name: str,
    description: str,
    vpc_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a security group in the specified VPC.
    
    This method creates a new security group or returns information
    about an existing group with the same name. It automatically
    retrieves the default VPC if no VPC ID is provided.
    
    Args:
        group_name: Name for the security group. Must be unique
            within the VPC.
        description: Human-readable description of the security
            group's purpose.
        vpc_id: VPC ID where the security group will be created.
            If None, uses the default VPC.
    
    Returns:
        Dictionary containing:
            - GroupId: The security group ID
            - GroupName: The security group name
            - Exists: Boolean indicating if group already existed
    
    Raises:
        ClientError: If AWS API call fails
        
    Example:
        >>> sg_manager = SecurityGroupManager(ec2_client)
        >>> result = sg_manager.create_security_group(
        ...     group_name='web-sg',
        ...     description='Web server security group'
        ... )
        >>> print(result['GroupId'])
        'sg-0123456789abcdef0'
    """
    pass
```

## 🔍 Code Review Process

Pull requests will be reviewed for:

1. **Functionality**: Does it work as intended?
2. **Code Quality**: Is it clean and maintainable?
3. **Documentation**: Is it well documented?
4. **Tests**: Are there adequate tests?
5. **Error Handling**: Are errors handled properly?
6. **Performance**: Are there any performance issues?
7. **Security**: Are there any security concerns?

## 🎨 Design Principles

### Modularity
- Each module should handle one AWS service
- Avoid tight coupling between modules
- Use dependency injection

### Error Handling
- Always handle specific exceptions
- Log errors with context
- Provide helpful error messages to users

### User Experience
- Provide progress feedback
- Use clear, informative messages
- Make it easy to understand what's happening

### Configuration
- Centralize configuration in `config.py`
- Use environment variables for secrets
- Provide sensible defaults

## 🚀 Feature Development

### Adding a New Module

1. **Create module file** in `modules/`
   ```python
   """
   AWS Service management module.
   """
   
   import logging
   from typing import Dict, Any
   import boto3
   
   logger = logging.getLogger(__name__)
   
   class ServiceManager:
       """Manages AWS Service."""
       
       def __init__(self, client):
           self.client = client
   ```

2. **Update `modules/__init__.py`**
   ```python
   from .service import ServiceManager
   
   __all__ = [..., 'ServiceManager']
   ```

3. **Add configuration** to `config.py`
   ```python
   # Service Configuration
   SERVICE_PARAM = "value"
   ```

4. **Update `deploy.py`** to use new module
   ```python
   from modules import ServiceManager
   
   self.service_manager = ServiceManager(self.client)
   ```

5. **Add documentation** in `DOCUMENTATION.md`

6. **Add tests** in `tests/`

### Example: Adding RDS Support

```python
# modules/rds.py
class RDSManager:
    """Manages RDS database instances."""
    
    def __init__(self, rds_client):
        self.rds_client = rds_client
    
    def create_db_instance(
        self,
        db_name: str,
        instance_class: str,
        engine: str = "mysql"
    ) -> Dict[str, Any]:
        """Create RDS database instance."""
        # Implementation
        pass
```

## 📋 Checklist

Before submitting a pull request:

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] Tests pass locally
- [ ] No new warnings
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

## 💡 Tips

### Debugging

```python
# Use logging for debugging, not print()
logger.debug(f"Variable value: {variable}")

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
```

### AWS API Testing

```python
# Use moto for testing AWS API calls
from moto import mock_ec2, mock_elbv2

@mock_ec2
def test_create_instance():
    # Your test code
    pass
```

### Local Testing

```bash
# Test without actually creating AWS resources
export AWS_DEFAULT_REGION=us-east-1
python -m pytest tests/ -v
```

## 🌟 Recognition

Contributors will be:
- Added to `CONTRIBUTORS.md`
- Mentioned in release notes
- Credited in the README

## 📞 Getting Help

- **Questions**: Open a [Discussion](https://github.com/yourusername/aws-boto3-automation/discussions)
- **Bug Reports**: Open an [Issue](https://github.com/yourusername/aws-boto3-automation/issues)
- **Security**: Email [security@yourdomain.com](mailto:security@yourdomain.com)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
