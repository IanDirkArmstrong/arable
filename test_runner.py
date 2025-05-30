#!/usr/bin/env python3
"""
Simple test runner for development
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n🔧 {description}")
    print(f"   Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"   ✅ Success")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {e}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"   ❌ Command not found: {cmd[0]}")
        return False


def main():
    """Run development tests"""
    print("🚀 Monday Automation Development Test Runner")

    # Check if we're in the right directory
    if not Path("src/monday_automation").exists():
        print("❌ Error: Run this from the monday_automation project root directory")
        sys.exit(1)

    tests = [
        # Basic setup tests
        (
            [
                "python",
                "-c",
                "import sys; sys.path.append('src'); import monday_automation; print('Import successful')",
            ],
            "Testing basic imports",
        ),
        # Config template test
        (
            ["python", "run.py", "init-config", "--output", "test_config.yaml"],
            "Testing config template creation",
        ),
        # CLI help test
        (["python", "run.py", "--help"], "Testing CLI help"),
        # Test suite (if pytest is available)
        (["python", "-m", "pytest", "--version"], "Checking pytest availability"),
    ]

    results = []
    for cmd, description in tests:
        results.append(run_command(cmd, description))

    # Try running pytest if available
    if results[-1]:  # pytest is available
        pytest_cmd = ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
        run_command(pytest_cmd, "Running test suite")

    # Summary
    passed = sum(results)
    total = len(results)

    print(f"\n📊 Test Summary: {passed}/{total} basic tests passed")

    if passed == total:
        print("🎉 All basic tests passed! Ready for development.")
    else:
        print("⚠️  Some tests failed. Check the output above.")

    # Cleanup
    test_files = ["test_config.yaml"]
    for file in test_files:
        if Path(file).exists():
            Path(file).unlink()
            print(f"🧹 Cleaned up {file}")


if __name__ == "__main__":
    main()
