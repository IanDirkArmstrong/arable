#!/usr/bin/env python3
"""
CLI entry point for Monday.com automation
"""

import sys
import os
from pathlib import Path

# Add src to Python path to allow running without installation
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

try:
    from src.monday_automation.main import cli
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Try installing the package: pip install -e .")
    print("💡 Or install dependencies: pip install -r requirements.txt")
    sys.exit(1)

if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        print("\n⚠️  Automation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Automation failed: {e}")
        print("💡 Run with --verbose for more details")
        sys.exit(1)
