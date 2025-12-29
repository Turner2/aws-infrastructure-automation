# Complete Setup Guide

This guide will walk you through setting up the AWS Infrastructure Automation project from scratch.

## 📋 Prerequisites Checklist

Before you begin, ensure you have:

- [ ] AWS Account (with admin access or appropriate IAM permissions)
- [ ] Python 3.8 or higher installed
- [ ] pip (Python package installer)
- [ ] Git installed
- [ ] Terminal/Command line access
- [ ] Text editor or IDE

## 🔧 Step 1: AWS Account Setup

### 1.1 Create AWS Account

If you don't have an AWS account:
1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click "Create an AWS Account"
3. Follow the registration process
4. Verify your email and payment method

### 1.2 Create IAM User

For security, create an IAM user instead of using root credentials:

1. **Log in to AWS Console**
   - Go to [console.aws.amazon.com](https://console.aws.amazon.com)

2. **Navigate to IAM**
   - Search for "IAM" in the services search bar
   - Click on "IAM"

3. **Create User**
   - Click "Users" in the left sidebar
   - Click "Add users"
   - Username: `boto3-automation-user`
   - Select "Programmatic access"
   - Click "Next: Permissions"

4. **Set Permissions**
   - Choose "Attach existing policies directly"
   - Search and select these policies:
     - `AmazonEC2FullAccess`
     - `ElasticLoadBalancingFullAccess`
     - `AmazonVPCReadOnlyAccess`
   - Click "Next: Tags"

5. **Add Tags** (Optional)
   - Key: `Purpose`, Value: `Boto3 Automation`
   - Click "Next: Review"

6. **Review and Create**
   - Review the settings
   - Click "Create user"

7. **Save Credentials** ⚠️ IMPORTANT
   - Download the CSV file or copy:
     - Access Key ID
     - Secret Access Key
   - Store these securely - you won't see them again!

## 🔧 Step 2: Local Environment Setup

### 2.1 Install Python

**macOS**:
```bash
# Check if Python is installed
python3 --version

# If not installed, use Homebrew
brew install python3
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Windows**:
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Click "Install Now"

### 2.2 Install Git

**macOS**:
```bash
brew install git
```

**Ubuntu/Debian**:
```bash
sudo apt install git
```

**Windows**:
Download from [git-scm.com](https://git-scm.com)

### 2.3 Verify Installations

```bash
python3 --version  # Should show 3.8 or higher
pip3 --version     # Should show pip version
git --version      # Should show git version
```

## 🔧 Step 3: AWS CLI Setup

### 3.1 Install AWS CLI

**macOS**:
```bash
brew install awscli
```

**Ubuntu/Debian**:
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

**Windows**:
Download installer from [AWS CLI Install Guide](https://aws.amazon.com/cli/)

### 3.2 Configure AWS CLI

```bash
aws configure
```

Enter your credentials when prompted:
```
AWS Access Key ID [None]: YOUR_ACCESS_KEY_ID
AWS Secret Access Key [None]: YOUR_SECRET_ACCESS_KEY
Default region name [None]: us-east-1
Default output format [None]: json
```

### 3.3 Test AWS CLI

```bash
# Test connection
aws sts get-caller-identity

# Should return your account info
```

## 🔧 Step 4: Project Setup

### 4.1 Clone Repository

```bash
# Create projects directory
mkdir -p ~/projects
cd ~/projects

# Clone the repository
git clone https://github.com/yourusername/aws-boto3-automation.git

# Navigate to project
cd aws-boto3-automation
```

### 4.2 Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment

# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# You should see (venv) in your prompt
```

### 4.3 Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Verify installations
pip list
```

Expected output should include:
- boto3
- botocore
- requests

## 🔧 Step 5: Configuration

### 5.1 Review Configuration

Open `config.py` in your editor:

```python
# Key settings to review:
TEMPLATE_NAME = "barista-cafe"  # Your project name
TEMPLATE_ID = "2137"            # Tooplate template ID
AWS_REGION = "us-east-1"        # Your AWS region
INSTANCE_TYPE = "t2.micro"      # Instance type (free tier)
```

### 5.2 Customize (Optional)

If you want to use a different template:
1. Browse [tooplate.com](https://www.tooplate.com)
2. Find a template you like
3. Note the template ID from the URL
4. Update `config.py`:
   ```python
   TEMPLATE_NAME = "your-template-name"
   TEMPLATE_ID = "template-id"
   ```

## 🚀 Step 6: First Deployment

### 6.1 Pre-Deployment Check

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check you're in the right directory
pwd  # Should end in /aws-boto3-automation

# Verify virtual environment is active
which python  # Should point to venv/bin/python
```

### 6.2 Run Deployment

```bash
# Run the deployment script
python deploy.py
```

You should see output like:
```
==========================================
  🚀 AWS Infrastructure Deployment
==========================================

Region: us-east-1
Template: barista-cafe

==========================================
  1️⃣  Creating Key Pair
==========================================
✓ Key Pair: barista-cafe-keypair
  ID: key-0123456789abcdef0
  💾 Private key saved to: barista-cafe-keypair.pem
  ⚠️  Keep this file safe! It cannot be recovered.

... (more output) ...

==========================================
🌐 ACCESS YOUR WEBSITE:
==========================================

   🔗 ALB Endpoint: http://barista-cafe-alb-123456789.us-east-1.elb.amazonaws.com
   🔗 Direct Access: http://54.123.45.67
   📊 Instance Info: http://barista-cafe-alb-123456789.us-east-1.elb.amazonaws.com/instance-info.html

⏰ Note: Allow 2-3 minutes for the website to be fully configured.
==========================================
```

### 6.3 Verify Deployment

1. **Wait 2-3 minutes** for the website setup to complete

2. **Open the ALB endpoint URL** in your browser

3. **Check AWS Console**:
   - EC2 Dashboard: See your instance
   - Load Balancers: See your ALB
   - Target Groups: See instance registered

### 6.4 Test Access

```bash
# SSH to instance (if needed)
chmod 400 barista-cafe-keypair.pem
ssh -i barista-cafe-keypair.pem ec2-user@YOUR_INSTANCE_IP

# Check web server logs
sudo tail -f /var/log/httpd/access_log
```

## 🧹 Step 7: Cleanup

When you're done testing:

```bash
# Run cleanup script
python cleanup.py

# Confirm when prompted
# Enter: yes

# Or force cleanup without confirmation
python cleanup.py --force
```

## ⚠️ Troubleshooting

### Issue: "No module named boto3"

**Solution**:
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Unable to locate credentials"

**Solution**:
```bash
# Reconfigure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### Issue: "UnauthorizedOperation"

**Solution**:
- Check IAM user has necessary permissions
- Verify policies are attached:
  - `AmazonEC2FullAccess`
  - `ElasticLoadBalancingFullAccess`

### Issue: "VPCIdNotSpecified"

**Solution**:
```bash
# Create default VPC if missing
aws ec2 create-default-vpc
```

### Issue: Website not loading after 5 minutes

**Solution**:
1. Check instance is running:
   ```bash
   aws ec2 describe-instances --filters "Name=tag:Name,Values=barista-cafe-instance"
   ```

2. Check user data execution:
   ```bash
   # SSH to instance
   ssh -i keypair.pem ec2-user@INSTANCE_IP
   
   # Check logs
   sudo cat /var/log/cloud-init-output.log
   sudo systemctl status httpd
   ```

3. Verify security groups:
   ```bash
   aws ec2 describe-security-groups --group-names barista-cafe-sg
   ```

### Issue: "Key pair already exists"

**Solution**:
The script handles this automatically. If you want to create a new one:
1. Delete existing key pair:
   ```bash
   aws ec2 delete-key-pair --key-name barista-cafe-keypair
   rm barista-cafe-keypair.pem
   ```
2. Run deployment again

## 📊 Cost Monitoring

### Check Current Costs

1. Go to [AWS Billing Console](https://console.aws.amazon.com/billing)
2. Click "Bills" in the left menu
3. Review current month's charges

### Set Up Cost Alerts

1. Go to [CloudWatch Console](https://console.aws.amazon.com/cloudwatch)
2. Click "Billing" in the left menu
3. Create alarm for spending threshold

### Expected Costs

With t2.micro (Free Tier):
- First 750 hours/month: **FREE**
- After free tier: ~$0.0116/hour

With ALB:
- ~$0.0225/hour (~$16/month)

**Total if left running**: ~$25/month

## 🎓 Next Steps

1. **Explore the Code**
   ```bash
   # Read the modules
   cat modules/ec2_instance.py
   cat modules/alb.py
   ```

2. **Try Modifications**
   - Change instance type
   - Use different template
   - Add more instances

3. **Add Features**
   - Add HTTPS support
   - Add Auto Scaling
   - Add RDS database

4. **Read Documentation**
   - `DOCUMENTATION.md` - Technical details
   - `EXAMPLES.md` - Configuration examples
   - `ARCHITECTURE.md` - System diagrams

## 📚 Additional Resources

### AWS Documentation
- [EC2 User Guide](https://docs.aws.amazon.com/ec2/)
- [ELB User Guide](https://docs.aws.amazon.com/elasticloadbalancing/)
- [VPC User Guide](https://docs.aws.amazon.com/vpc/)

### Boto3 Documentation
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [EC2 Examples](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/ec2-examples.html)

### Learning Resources
- [AWS Free Tier](https://aws.amazon.com/free/)
- [AWS Training](https://aws.amazon.com/training/)
- [Python Official Docs](https://docs.python.org/3/)

## ✅ Success Checklist

After completing this guide, you should have:

- [ ] AWS account set up
- [ ] IAM user created with proper permissions
- [ ] AWS CLI installed and configured
- [ ] Python virtual environment created
- [ ] Project dependencies installed
- [ ] Successfully deployed infrastructure
- [ ] Accessed the deployed website
- [ ] Successfully cleaned up resources

## 💬 Getting Help

If you encounter issues:

1. **Check Logs**
   ```bash
   # Application logs
   tail -f deploy.log
   
   # AWS CloudWatch logs
   # (if configured)
   ```

2. **Search Issues**
   - Check GitHub Issues
   - Search Stack Overflow

3. **Ask for Help**
   - Open a GitHub Issue
   - Provide error messages
   - Include AWS region
   - Include Python version

## 🎉 Congratulations!

You've successfully set up and deployed AWS infrastructure using Python and Boto3!

---

**Last Updated**: December 2025
