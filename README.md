# AWS Infrastructure Automation with Boto3

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![AWS](https://img.shields.io/badge/AWS-boto3-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Tests](https://img.shields.io/badge/tests-45%20passed-success.svg)
![Coverage](https://img.shields.io/badge/coverage-56%25-yellow.svg)

A production-ready, modular Python automation framework for deploying complete AWS infrastructure using Boto3. This project demonstrates infrastructure-as-code principles with clean architecture, comprehensive error handling, professional DevOps practices, and a complete test suite.

## 🎯 Features

- **🔑 Key Pair Management**: Automated EC2 key pair creation and secure storage
- **🛡️ Security Groups**: Dynamic security group configuration with IP-based rules
- **💻 EC2 Instances**: Automated instance provisioning with custom user data
- **⚖️ Application Load Balancer**: Full ALB setup with target groups and listeners
- **🌐 Web Server Deployment**: Automatic website deployment from tooplate.com templates
- **🧹 Resource Cleanup**: Comprehensive cleanup script for safe resource removal
- **📊 Modular Architecture**: Clean, maintainable code structure following best practices
- **🧪 Comprehensive Testing**: 45 unit and integration tests with 56% code coverage
- **🔄 CI/CD Ready**: GitHub Actions workflow for automated testing and deployment

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Application Load Balancer            │
│                  (Internet-facing, Multi-AZ)            │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │   Target Group       │
            │   (Health Checks)    │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │   EC2 Instance       │
            │   - t2.micro         │
            │   - Amazon Linux 2023│
            │   - Apache Webserver │
            └──────────────────────┘
```

## 📁 Project Structure

```
aws-infrastructure-automation/
├── deploy.py                 # Main deployment orchestration
├── cleanup.py               # Resource cleanup script
├── config.py                # Configuration and settings
├── requirements.txt         # Python dependencies
│
├── modules/                # Core AWS service modules
│   ├── __init__.py
│   ├── keypair.py         # Key pair management
│   ├── security_group.py  # Security group operations
│   ├── ec2_instance.py    # EC2 instance management
│   └── alb.py            # Application Load Balancer
│
├── utils/                 # Helper utilities
│   ├── __init__.py
│   └── helpers.py        # Common utility functions
│
├── tests/                 # Test suite
│   ├── test_config.py     # Configuration tests
│   ├── test_modules.py    # AWS module tests
│   ├── test_utils.py      # Utility tests
│   ├── test_integration.py # Integration tests
│   └── run_tests.py       # Test runner
│
├── .github/              # GitHub Actions CI/CD
│   └── workflows/
│       ├── python-lint.yml
│       └── tests.yml     # Automated testing
│
├── quick-deploy.sh       # Quick deployment script
├── quick-cleanup.sh      # Quick cleanup script
├── quick-test.sh         # Quick test execution
│
└── docs/                # Documentation
    ├── README.md
    ├── DOCUMENTATION.md
    ├── EXAMPLES.md
    ├── ARCHITECTURE.md
    ├── SETUP_GUIDE.md
    ├── TESTING.md       # Testing documentation
    └── CONTRIBUTING.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Boto3 library

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/aws-infrastructure-automation.git
   cd aws-infrastructure-automation
   ```

2. **Set up virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run tests** (optional but recommended)

   ```bash
   ./quick-test.sh
   # or
   python run_tests.py
   ```

5. **Configure AWS credentials**
   ```bash
   aws configure
   ```

### Configuration

Edit `config.py` to customize your deployment:

```python
# Template Configuration
TEMPLATE_NAME = "barista-cafe"  # Change to your preferred template name
TEMPLATE_ID = "2137"            # Tooplate template ID

# AWS Configuration
AWS_REGION = "us-east-1"        # Your preferred AWS region

# EC2 Configuration
INSTANCE_TYPE = "t2.micro"      # Instance type
```

### Deployment

**Deploy the infrastructure:**

```bash
python deploy.py
```

Or use the quick deploy script:

```bash
./quick-deploy.sh
```

**Note:** The script automatically:
- Detects and uses available subnets in your VPC
- Configures networking properly to avoid conflicts
- Handles security groups correctly

The script will:

1. ✅ Create an EC2 key pair
2. ✅ Retrieve your public IP address
3. ✅ Create security groups for EC2 and ALB
4. ✅ Launch an EC2 instance with a web server
5. ✅ Set up an Application Load Balancer
6. ✅ Configure target groups and listeners
7. ✅ Display access URLs

**Example Output:**

```
==========================================
🌐 ACCESS YOUR WEBSITE:
==========================================

   🔗 ALB Endpoint: http://barista-cafe-alb-123456789.us-east-1.elb.amazonaws.com
   🔗 Direct Access: http://54.123.45.67
   📊 Instance Info: http://barista-cafe-alb-123456789.us-east-1.elb.amazonaws.com/instance-info.html

⏰ Note: Allow 2-3 minutes for the website to be fully configured.
==========================================
```

### Cleanup

**Remove all resources:**

```bash
python cleanup.py
```

**Force cleanup (skip confirmation):**

```bash
python cleanup.py --force
```

## 📚 Documentation

- **[SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** - Complete setup instructions
- **[DOCUMENTATION.md](docs/DOCUMENTATION.md)** - Technical documentation and API reference
- **[EXAMPLES.md](docs/EXAMPLES.md)** - Configuration examples and use cases
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture diagrams
- **[TESTING.md](docs/TESTING.md)** - Complete testing guide
- **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** - Contribution guidelines
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project overview and highlights
- **[TEST_REPORT.md](TEST_REPORT.md)** - Latest test results and coverage

## 🛡️ Security Features

- **IP Whitelisting**: SSH access restricted to your public IP
- **Key Pair Protection**: Private keys saved with restricted permissions (chmod 400)
- **Security Groups**: Principle of least privilege
- **Resource Tagging**: All resources tagged for tracking and cost management
- **Automated Cleanup**: Prevents resource waste and unauthorized access

## 🧪 Testing

### Test Suite

This project includes a comprehensive test suite with **45 tests** covering all major components:

```bash
# Run all tests
./quick-test.sh

# Run with unittest
python run_tests.py

# Run with pytest and coverage
pytest test_*.py -v --cov=. --cov-report=html
```

### Test Coverage

| Component | Tests | Coverage | Status |
|-----------|-------|----------|--------|
| Configuration | 10 | 100% | ✅ |
| AWS Modules | 17 | 41-65% | ✅ |
| Utilities | 10 | 97% | ✅ |
| Integration | 10 | - | ✅ |
| **Total** | **45** | **56%** | ✅ |

### What's Tested

- ✅ **Configuration Management**: All settings and resource names
- ✅ **AWS Modules**: KeyPair, SecurityGroup, EC2, ALB managers
- ✅ **Utility Functions**: IP retrieval, formatting, progress indicators
- ✅ **Integration Workflows**: Complete deployment scenarios
- ✅ **Error Handling**: Exception handling and edge cases

### Test Features

- **Fast**: Complete test suite runs in < 1 second
- **Isolated**: All AWS SDK calls properly mocked
- **CI/CD Ready**: Automated testing via GitHub Actions
- **Well Documented**: See [TESTING.md](docs/TESTING.md) for details

### Continuous Integration

Tests automatically run on:
- Every push to main/develop branches
- Every pull request
- Multiple Python versions (3.8-3.12)

The project includes error handling for:

- ✅ Missing AWS credentials
- ✅ Insufficient permissions
- ✅ Resource conflicts
- ✅ Network issues
- ✅ Service quotas

## 📊 Modules Overview

### KeyPairManager (`modules/keypair.py`)

- Create and manage EC2 key pairs
- Secure private key storage
- Key pair existence checking

### SecurityGroupManager (`modules/security_group.py`)

- Create security groups
- Configure ingress rules dynamically
- VPC integration

### EC2InstanceManager (`modules/ec2_instance.py`)

- AMI selection and filtering
- Instance provisioning with user data
- Auto-assign public IP
- Instance state management

### ALBManager (`modules/alb.py`)

- Application Load Balancer creation
- Target group configuration
- Multi-AZ subnet selection
- Listener and health check setup

## 🎨 Customization

### Change Website Template

Edit `config.py`:

```python
TEMPLATE_NAME = "your-template-name"
TEMPLATE_ID = "1234"  # From tooplate.com
```

### Modify Instance Type

```python
INSTANCE_TYPE = "t2.small"  # Or any other EC2 instance type
```

### Change Region

```python
AWS_REGION = "eu-west-1"
```

## 📝 Best Practices Demonstrated

1. **Modular Design**: Separation of concerns across modules
2. **Configuration Management**: Centralized configuration
3. **Error Handling**: Comprehensive exception handling
4. **Logging**: Structured logging for debugging
5. **Resource Cleanup**: Clean teardown procedures
6. **Documentation**: Inline comments and docstrings
7. **Type Hints**: Python type annotations for better code quality
8. **DRY Principle**: Reusable utility functions
9. **Test Coverage**: Unit and integration tests with mocking
10. **CI/CD Pipeline**: Automated testing and quality checks

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Before Submitting

1. **Run tests**: `./quick-test.sh` - All tests must pass
2. **Check coverage**: Maintain or improve code coverage
3. **Update docs**: Add documentation for new features
4. **Follow style**: Use existing code style and conventions

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Website templates from [Tooplate.com](https://www.tooplate.com/)
- AWS Boto3 Documentation
- Python community

## 💡 Use Cases

- **Learning AWS**: Perfect for understanding AWS services programmatically
- **DevOps Practice**: Infrastructure automation patterns and testing
- **Quick Deployments**: Rapid prototype hosting
- **Portfolio Project**: Demonstrate AWS, Python, and testing skills
- **Interview Prep**: Shows professional coding practices

## 🔍 Troubleshooting

### Common Issues

**"InvalidParameterCombination: Network interfaces and an instance-level security groups may not be specified"**

- This has been fixed in the latest version
- The code now properly specifies security groups only in NetworkInterfaces
- Pull the latest code if you encounter this

**"No subnets found for the default VPC"**

- The code automatically detects and uses available subnets
- If your VPC has no subnets, create them in AWS Console:
  - Go to VPC Dashboard → Subnets → Create Subnet
  - Or the code will automatically find existing subnets in your VPC

**"No default VPC found"**

- Create a default VPC in your AWS console
- Or specify a VPC ID in the security group configuration

**"Insufficient permissions"**

- Ensure your IAM user/role has these permissions:
  - `ec2:*` (EC2 full access)
  - `elasticloadbalancing:*` (ELB full access)
- Or attach the `AmazonEC2FullAccess` and `ElasticLoadBalancingFullAccess` policies

**Website not loading**

- Wait 2-3 minutes for user data script to complete
- Check security group rules
- Verify instance status checks

**Tests failing**

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Run from project root directory
- Check Python version (3.8+ required)

See [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) and [TESTING.md](docs/TESTING.md) for more troubleshooting help.

## 💰 Cost Estimation

With t2.micro (Free Tier eligible):

- Instance: ~$8.50/month (after free tier)
- ALB: ~$16/month
- **Total: ~$25/month** with minimal traffic

---

**⭐ If you find this project helpful, please consider giving it a star!**
