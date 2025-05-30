#!/usr/bin/env python3
"""
Final validation that everything is working before production use
"""

import sys
from pathlib import Path

sys.path.append("src")


def final_validation():
    """Run comprehensive validation"""
    print("🔍 Final Validation Checklist")
    print("=" * 30)

    results = []

    # Test 1: Import validation
    try:
        from monday_automation.main import ProjectAutomation
        from monday_automation.config import load_config

        print("✅ 1. Imports working")
        results.append(True)
    except Exception as e:
        print(f"❌ 1. Import failed: {e}")
        results.append(False)

    # Test 2: Configuration validation
    try:
        config = load_config("config/config.yaml")
        print("✅ 2. Configuration loads")
        results.append(True)
    except Exception as e:
        print(f"❌ 2. Config failed: {e}")
        results.append(False)
        return False  # Can't continue without config

    # Test 3: Monday API connection
    try:
        from monday_automation.monday_api import MondayAPI
        from monday_automation.logger import setup_logger

        logger = setup_logger("validation", "INFO")
        api = MondayAPI(config.monday.api_token, logger)

        # Test basic query
        result = api.make_request("query { me { name } }")
        if "data" in result:
            print("✅ 3. Monday.com API connected")
            results.append(True)
        else:
            print(f"❌ 3. Monday API failed: {result}")
            results.append(False)
    except Exception as e:
        print(f"❌ 3. Monday API error: {e}")
        results.append(False)

    # Test 4: Google Sheets connection
    try:
        from monday_automation.google_sheets import GoogleSheetsClient

        sheets_client = GoogleSheetsClient(
            config.google_sheets.credentials_path,
            config.google_sheets.sheet_name,
            logger,
        )
        sheets_client.connect()
        print("✅ 4. Google Sheets connected")
        results.append(True)
    except Exception as e:
        print(f"❌ 4. Google Sheets error: {e}")
        results.append(False)

    # Test 5: Data loading
    try:
        projects, milestones = sheets_client.read_data()
        if projects and milestones:
            print(
                f"✅ 5. Data loaded ({len(projects)} projects, {len(milestones)} milestones)"
            )
            results.append(True)
        else:
            print("❌ 5. No data found")
            results.append(False)
    except Exception as e:
        print(f"❌ 5. Data loading error: {e}")
        results.append(False)

    # Test 6: Milestone validation
    try:
        milestone_types = set(m.get("MileStoneType", "").strip() for m in milestones)
        milestone_types.discard("")

        mapped_types = set(config.milestone_mappings["phase"].keys())
        unmapped = milestone_types - mapped_types

        if not unmapped:
            print("✅ 6. All milestone types mapped")
            results.append(True)
        else:
            print(f"⚠️  6. Unmapped milestone types: {len(unmapped)}")
            for milestone_type in sorted(unmapped):
                print(f"     - {milestone_type}")
            results.append(False)
    except Exception as e:
        print(f"❌ 6. Milestone validation error: {e}")
        results.append(False)

    # Summary
    passed = sum(results)
    total = len(results)

    print(f"\n📊 Validation Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Ready for production use.")
        print("\n🚀 To run the automation:")
        print("   python run.py run --test-project [PROJECT_NUMBER] --verbose")
        print("   python run.py run  # Process all projects")
        return True
    else:
        print("⚠️  Some tests failed. Fix issues before production use.")
        print("\n💡 Common fixes:")
        print("   - Update config/config.yaml with correct credentials")
        print("   - Check Google Sheets permissions")
        print("   - Verify Monday.com board IDs")
        print("   - Add missing milestone mappings")
        return False


if __name__ == "__main__":
    success = final_validation()
    sys.exit(0 if success else 1)
