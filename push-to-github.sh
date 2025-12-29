#!/bin/bash
# GitHub Push Script for AWS Infrastructure Automation

echo "🚀 Pushing to GitHub..."
echo ""

# Check if we're in the right directory
if [ ! -f "deploy.py" ]; then
    echo "❌ Error: Please run this from the project root directory"
    exit 1
fi

echo "📋 Step 1: Go to https://github.com/new"
echo ""
echo "   Create a new repository with these settings:"
echo "   - Name: aws-infrastructure-automation"
echo "   - Description: Production-ready Python automation for AWS infrastructure using Boto3"
echo "   - Public ✓"
echo "   - Do NOT initialize with README, .gitignore, or license"
echo ""
read -p "Press ENTER after you've created the repository..."

echo ""
echo "📝 Step 2: Enter your GitHub username:"
read -p "Username: " github_username

echo ""
echo "🔗 Step 3: Adding remote and pushing..."

# Add remote
git remote add origin "https://github.com/${github_username}/aws-infrastructure-automation.git"

# Push to GitHub
git branch -M main
git push -u origin main

echo ""
echo "✅ Done! Your repository is now at:"
echo "   https://github.com/${github_username}/aws-infrastructure-automation"
echo ""
echo "🎯 Next steps:"
echo "   1. Add topics/tags: aws, boto3, python, infrastructure-as-code, devops"
echo "   2. Enable Issues in repository settings"
echo "   3. Star your own repo ⭐"
echo ""
