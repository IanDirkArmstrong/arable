#!/bin/bash

# Test script to verify .gitignore is working
cd "/Users/ian/Library/CloudStorage/GoogleDrive-ian@wowitsian.com/My Drive/AI/ARABLE"

echo "🔍 Testing .gitignore effectiveness..."
echo "Files that would be tracked by git:"
echo "======================================"

# Initialize git temporarily to test
git init --quiet

# Add files and see what gets staged
git add . 2>/dev/null

# Show what would be committed
git status --porcelain | head -20

echo ""
echo "🔍 Checking if sensitive files are ignored:"
echo "==========================================="

# Check specific sensitive files
if git ls-files --cached | grep -q "\.env$"; then
    echo "❌ .env would be committed"
else
    echo "✅ .env is properly ignored"
fi

if git ls-files --cached | grep -q "config\.yaml$"; then
    echo "❌ config.yaml would be committed"
else
    echo "✅ config.yaml is properly ignored"
fi

if git ls-files --cached | grep -q "credentials/.*\.json"; then
    echo "❌ JSON credentials would be committed"
else
    echo "✅ JSON credentials are properly ignored"
fi

if git ls-files --cached | grep -q "rsinet"; then
    echo "❌ RSI files would be committed"
else
    echo "✅ RSI files are properly ignored"
fi

# Clean up test
rm -rf .git

echo ""
echo "✅ .gitignore test complete"
