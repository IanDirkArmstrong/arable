#!/bin/bash

# Refactor ARABLE to lowercase "arable" throughout codebase
# Preserves branding in markdown headings only

set -e

echo "🔧 Refactoring ARABLE to lowercase 'arable'..."

# Define the base directory (adjust if running from different location)
if [ -d "/Users/ian/development/arable" ]; then
    BASE_DIR="/Users/ian/development/arable"
elif [ -d "/Users/ian/Library/CloudStorage/GoogleDrive-ian@wowitsian.com/My Drive/AI/ARABLE" ]; then
    BASE_DIR="/Users/ian/Library/CloudStorage/GoogleDrive-ian@wowitsian.com/My Drive/AI/ARABLE"
else
    echo "❌ Could not find ARABLE directory"
    exit 1
fi

echo "📁 Working in: $BASE_DIR"
cd "$BASE_DIR"

# Function to refactor Python files
refactor_python() {
    echo "🐍 Refactoring Python files..."
    
    # Files to update
    find . -name "*.py" -not -path "./docs/*" | while read file; do
        echo "  Processing: $file"
        
        # Use sed to replace ARABLE with arable in various contexts
        sed -i.bak \
            -e 's/ARABLE CLI/arable CLI/g' \
            -e 's/ARABLE system/arable system/g' \
            -e 's/ARABLE automation/arable automation/g' \
            -e 's/ARABLE project/arable project/g' \
            -e 's/ARABLE Agent/arable Agent/g' \
            -e 's/ARABLE Agents/arable Agents/g' \
            -e 's/Starting Monday\.com Project Automation/Starting arable project automation/g' \
            -e 's/Show ARABLE system information/Show arable system information/g' \
            -e 's/Manage and execute ARABLE agents/Manage and execute arable agents/g' \
            -e 's/Run ARABLE agent demonstrations/Run arable agent demonstrations/g' \
            -e 's/arable Agent Demo/arable agent demo/g' \
            -e 's/\[bold blue\]ARABLE\[\/bold blue\]/[bold blue]arable[\/bold blue]/g' \
            -e 's/🤖 ARABLE Agents/🤖 arable agents/g' \
            -e 's/🎬 ARABLE Agent Demo/🎬 arable agent demo/g' \
            "$file"
        
        # Remove backup files
        rm -f "${file}.bak"
    done
}

# Function to refactor config files
refactor_config() {
    echo "⚙️  Refactoring config files..."
    
    # Update YAML files (but not the ones with RSI data in comments)
    find . -name "*.yaml" -o -name "*.yml" | grep -v docs | while read file; do
        echo "  Processing: $file"
        
        sed -i.bak \
            -e 's/# ARABLE Configuration/# arable configuration/g' \
            -e 's/ARABLE Environment/arable environment/g' \
            "$file"
            
        rm -f "${file}.bak"
    done
    
    # Update .env.example
    if [ -f ".env.example" ]; then
        echo "  Processing: .env.example"
        sed -i.bak \
            -e 's/# ARABLE Environment Variables/# arable environment variables/g' \
            ".env.example"
        rm -f ".env.example.bak"
    fi
}

# Function to refactor scripts
refactor_scripts() {
    echo "📜 Refactoring scripts..."
    
    find . -name "*.sh" -not -path "./docs/*" | while read file; do
        echo "  Processing: $file"
        
        sed -i.bak \
            -e 's/ARABLE Git Setup/arable git setup/g' \
            -e 's/Setting up ARABLE for Git/Setting up arable for git/g' \
            -e 's/ARABLE successfully moved/arable successfully moved/g' \
            -e 's/Testing \.gitignore effectiveness/Testing .gitignore effectiveness/g' \
            -e 's/✅ \.gitignore test complete/✅ .gitignore test complete/g' \
            "$file"
            
        rm -f "${file}.bak"
    done
}

# Function to refactor project metadata (but preserve proper names)
refactor_metadata() {
    echo "📋 Refactoring project metadata..."
    
    # Update pyproject.toml description (but keep name lowercase)
    if [ -f "pyproject.toml" ]; then
        echo "  Processing: pyproject.toml"
        sed -i.bak \
            -e 's/description = "Agentic Runtime And Business Logic Engine"/description = "agentic runtime and business logic engine"/g' \
            "pyproject.toml"
        rm -f "pyproject.toml.bak"
    fi
    
    # Update setup scripts
    find . -name "setup*.py" -not -path "./docs/*" | while read file; do
        echo "  Processing: $file"
        sed -i.bak \
            -e 's/ARABLE/arable/g' \
            "$file"
        rm -f "${file}.bak"
    done
}

# Function to update imports and module references
refactor_imports() {
    echo "📦 Checking imports (should already be lowercase)..."
    
    # The imports should already be correct since the package name is "arable"
    # Just double-check that we don't have any uppercase references
    find . -name "*.py" -not -path "./docs/*" | xargs grep -l "import.*ARABLE" | while read file; do
        echo "  ⚠️  Found uppercase import in: $file"
        sed -i.bak 's/import.*ARABLE/import arable/g' "$file"
        rm -f "${file}.bak"
    done
}

# Run all refactoring functions
refactor_python
refactor_config  
refactor_scripts
refactor_metadata
refactor_imports

echo ""
echo "✅ Refactoring complete!"
echo ""
echo "📊 Summary of changes:"
echo "  • CLI help text: 'ARABLE' → 'arable'"
echo "  • Console output: 'ARABLE' → 'arable'"
echo "  • Configuration comments: 'ARABLE' → 'arable'" 
echo "  • Script descriptions: 'ARABLE' → 'arable'"
echo "  • Project description: capitalized → lowercase"
echo ""
echo "🔍 Preserved:"
echo "  • Package name: 'arable' (already correct)"
echo "  • Import statements: 'arable' (already correct)"
echo "  • Documentation files: unchanged (as requested)"
echo ""
echo "🚀 Ready for git commit!"
