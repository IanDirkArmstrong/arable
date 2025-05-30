#!/bin/bash

# Initialize git repository for ARABLE project
cd "/Users/ian/Library/CloudStorage/GoogleDrive-ian@wowitsian.com/My Drive/AI/ARABLE"

echo "Initializing git repository..."
git init

echo "Setting up git configuration..."
git config user.name "Ian Dirk Armstrong"
git config user.email "ian@wowitsian.com"

echo "Adding initial files..."
git add .

echo "Creating initial commit..."
git commit -m "Initial commit: ARABLE multi-agent system

- Complete CLI implementation with Rich UI
- Agent infrastructure with registry, orchestrator, memory
- Monday.com and Google Sheets integrations
- Comprehensive documentation structure
- Testing framework and configuration management
- Hybrid CLI-agent architecture for progressive automation"

echo "Git repository initialized successfully!"
echo ""
echo "Next steps:"
echo "1. Create GitHub repository"
echo "2. Add remote origin: git remote add origin <github-url>"
echo "3. Push to GitHub: git push -u origin main"
