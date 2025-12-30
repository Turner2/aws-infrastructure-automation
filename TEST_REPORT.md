# Test Coverage Report

## Overview

Total test coverage for the AWS infrastructure automation modules.

**Last Run:** December 2025  
**Status:** All tests passing

## Coverage Summary

| Module                    | Coverage | Tests  |
| ------------------------- | -------- | ------ |
| config.py                 | 100%     | 10     |
| utils/helpers.py          | 97%      | 10     |
| modules/ec2_instance.py   | 65%      | 4      |
| modules/security_group.py | 64%      | 4      |
| modules/keypair.py        | 56%      | 3      |
| modules/alb.py            | 41%      | 4      |
| Integration               | -        | 10     |
| **Total**                 | **56%**  | **45** |

_Note: Main scripts (deploy.py, cleanup.py) excluded as they require AWS credentials for testing._

## Test Results

```
45 passed in 0.43s
```

### By Category

**Configuration (10 tests)**

- AWS region and settings validation
- Resource naming conventions
- User data script generation
- Security group rule definitions

**AWS Modules (17 tests)**

- KeyPair manager operations
- Security group creation and management
- EC2 instance lifecycle
- ALB and target group setup

**Utilities (10 tests)**

- IP address retrieval
- Output formatting
- Error handling

**Integration (8 tests)**

- End-to-end workflows
- Resource cleanup
- Error propagation

## Running Tests

```bash
# Run all tests
python run_tests.py

# With coverage
pytest test_*.py --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

## CI/CD

Tests run automatically on every push via GitHub Actions across Python 3.8-3.12.
