## Environment Setup

### Development Environment

**Option 1: Automated Setup (Recommended)**
```bash
# Clone/navigate to ARABLE directory
cd /path/to/arable

# Run setup script (creates virtual environment, installs dependencies)
python scripts/setup_dev.py

# Activate environment
source arable_env/bin/activate      # macOS/Linux
# or
arable_env\Scripts\activate         # Windows

# Verify installation
arable info
```

**Option 2: Manual Setup**
```bash
# Create virtual environment
python -m venv arable_env
source arable_env/bin/activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Verify
arable --help
```