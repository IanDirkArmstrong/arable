"""Monday.com Project and Milestone Automation Package"""

__version__ = "1.0.0"
__author__ = "Ian Armstrong"

# Make main classes available at package level
from .main import ProjectAutomation
from .config import load_config, Config
from .monday_api import MondayAPI
from .google_sheets import GoogleSheetsClient

__all__ = [
    "ProjectAutomation",
    "load_config",
    "Config",
    "MondayAPI",
    "GoogleSheetsClient",
]
