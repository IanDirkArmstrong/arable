#!/usr/bin/env python3
"""
Quick development environment setup
"""

import subprocess
import sys
from pathlib import Path


def setup_project():
    """Set up the development environment"""
    print("🔧 Setting up Monday Automation development environment...")

    # Create directories
    dirs = ["src/monday_automation", "tests", "config", "logs"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {dir_path}")

    # Create __init__.py files
    init_files = ["src/monday_automation/__init__.py", "tests/__init__.py"]

    for init_file in init_files:
        if not Path(init_file).exists():
            Path(init_file).touch()
            print(f"📄 Created: {init_file}")

    # Install dependencies if requirements.txt exists
    if Path("requirements.txt").exists():
        print("📦 Installing dependencies...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                check=True,
            )
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")

    # Create config template
    if not Path("config/config.yaml").exists():
        print("⚙️ Creating configuration template...")
        try:
            subprocess.run([sys.executable, "run.py", "init-config"], check=True)
            print("✅ Configuration template created")
        except subprocess.CalledProcessError:
            print("❌ Failed to create config template")

    print("\n🎉 Setup complete!")
    print("📝 Next steps:")
    print("   1. Edit config/config.yaml with your API credentials")
    print("   2. Run: python test_runner.py")
    print("   3. Run: python run.py run --help")


if __name__ == "__main__":
    setup_project()
