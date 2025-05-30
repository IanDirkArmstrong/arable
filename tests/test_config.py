"""Tests for configuration management"""

import pytest
import tempfile
import os
from pathlib import Path
import yaml
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from monday_automation.config import (
    load_config,
    validate_config,
    find_config_file,
    resolve_path,
    Config,
    ConfigError,
)


class TestConfigLoading:
    """Test configuration loading functionality"""

    def test_load_valid_config(self, temp_config_file, temp_credentials_file):
        """Test loading a valid configuration file"""
        # Update config to point to temp credentials
        config_dir = Path(temp_config_file).parent
        with open(temp_config_file, "r") as f:
            config_data = yaml.safe_load(f)

        config_data["google_sheets"]["credentials_path"] = temp_credentials_file

        with open(temp_config_file, "w") as f:
            yaml.dump(config_data, f)

        config = load_config(temp_config_file)

        assert isinstance(config, Config)
        assert config.monday.api_token == "test_token_123"
        assert config.monday.master_board_id == "123456789"
        assert config.google_sheets.sheet_name == "Test Sheet"
        assert "Kickoff" in config.milestone_mappings["phase"]

    def test_load_nonexistent_config(self):
        """Test loading a non-existent configuration file"""
        with pytest.raises(ConfigError, match="Config file not found"):
            load_config("nonexistent.yaml")

    def test_load_invalid_yaml(self):
        """Test loading invalid YAML"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            f.name

        try:
            with pytest.raises(ConfigError, match="Invalid YAML"):
                load_config(f.name)
        finally:
            os.unlink(f.name)

    def test_load_missing_required_keys(self):
        """Test loading config with missing required keys"""
        config_data = {"monday": {"api_token": "test"}}  # Missing other required keys

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            f.name

        try:
            with pytest.raises(ConfigError, match="Missing required config key"):
                load_config(f.name)
        finally:
            os.unlink(f.name)


class TestConfigValidation:
    """Test configuration validation"""

    def test_validate_valid_config(self, temp_config_file, temp_credentials_file):
        """Test validating a valid configuration"""
        # Update config to point to temp credentials
        with open(temp_config_file, "r") as f:
            config_data = yaml.safe_load(f)

        config_data["google_sheets"]["credentials_path"] = temp_credentials_file

        with open(temp_config_file, "w") as f:
            yaml.dump(config_data, f)

        config = load_config(temp_config_file)
        validate_config(config)  # Should not raise

    def test_validate_missing_api_token(self, temp_config_file):
        """Test validation with missing API token"""
        with open(temp_config_file, "r") as f:
            config_data = yaml.safe_load(f)

        config_data["monday"]["api_token"] = ""

        with open(temp_config_file, "w") as f:
            yaml.dump(config_data, f)

        config = load_config(temp_config_file)

        with pytest.raises(ConfigError, match="API token is required"):
            validate_config(config)

    def test_validate_missing_credentials_file(self, temp_config_file):
        """Test validation with missing credentials file"""
        config = load_config(temp_config_file)

        with pytest.raises(ConfigError, match="credentials file not found"):
            validate_config(config)


class TestPathResolution:
    """Test path resolution functionality"""

    def test_resolve_absolute_path(self):
        """Test resolving absolute paths"""
        abs_path = "/absolute/path/file.json"
        config_dir = Path("/config/dir")

        result = resolve_path(abs_path, config_dir)
        assert result == abs_path

    def test_resolve_relative_path(self):
        """Test resolving relative paths"""
        rel_path = "relative/file.json"
        config_dir = Path("/config/dir")

        result = resolve_path(rel_path, config_dir)
        expected = str((config_dir / rel_path).resolve())
        assert result == expected
