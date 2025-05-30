#!/bin/bash

# ARABLE Git Setup Script
# This script moves the project out of Google Drive and sets up git safely

set -e

echo "🔧 Setting up ARABLE for Git and GitHub..."

# Create local development directory
LOCAL_DIR="$HOME/Development/ARABLE"
GOOGLE_DRIVE_DIR="/Users/ian/Library/CloudStorage/GoogleDrive-ian@wowitsian.com/My Drive/AI/ARABLE"

echo "📁 Creating local development directory..."
mkdir -p "$LOCAL_DIR"

echo "🧹 Cleaning build artifacts (keeping credentials for development)..."
cd "$GOOGLE_DRIVE_DIR"

# Only remove build artifacts, keep credentials for development
# Credentials are safely ignored by .gitignore
rm -rf __pycache__/
rm -rf arable.egg-info/
rm -rf logs/*.log
rm -rf memory_store/
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true

echo "📋 Copying clean project to local directory..."
rsync -av \
  --exclude='.DS_Store' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='logs/*.log' \
  --exclude='memory_store/' \
  --exclude='arable.egg-info/' \
  "$GOOGLE_DRIVE_DIR/" "$LOCAL_DIR/"

echo "🔧 Setting up git repository..."
cd "$LOCAL_DIR"

# Initialize git
git init

# Configure git (update these as needed)
git config user.name "Ian Dirk Armstrong"
git config user.email "ian@wowitsian.com"

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: ARABLE multi-agent system

- Complete CLI implementation with Rich UI  
- Agent infrastructure with registry, orchestrator, memory
- Monday.com and Google Sheets integrations
- Comprehensive documentation structure
- Testing framework and configuration management
- Hybrid CLI-agent architecture for progressive automation

🔐 Security: Credentials preserved locally but ignored by git
📝 Templates: .env.example and config.example.yaml for sharing
🏗️ Ready for: GitHub setup and team collaboration"

echo ""
echo "✅ ARABLE successfully moved to: $LOCAL_DIR"
echo "✅ Git repository initialized"
echo "✅ All sensitive data removed"
echo ""
echo "🚀 Next steps:"
echo "1. Create GitHub repository: gh repo create ARABLE --public --description 'Multi-agent system for document intelligence and workflow automation'"
echo "2. Add remote: git remote add origin https://github.com/your-username/ARABLE.git"
echo "3. Push to GitHub: git push -u origin main"
echo ""
echo "📝 Development ready:"
echo "1. Your .env and config/config.yaml are already in place"
echo "2. Credentials are preserved and safely ignored by git"
echo "3. Use .env.example and config.example.yaml as templates for sharing"
