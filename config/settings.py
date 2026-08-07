"""
Application Settings

Central location for application-wide configuration.
"""

# Standard library imports
from pathlib import Path


# ==========================================================
# Project Paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CONFIG_DIR = PROJECT_ROOT / "config"

RULES_FILE = CONFIG_DIR / "rules.yaml"

ALIASES_FILE = CONFIG_DIR / "aliases.yaml"


# ==========================================================
# Upload Settings
# ==========================================================

SUPPORTED_FILE_TYPES = (
    ".csv",
    ".xlsx",
)


# ==========================================================
# Application Settings
# ==========================================================

APP_NAME = "Retail Analytics Dashboard"

APP_VERSION = "1.0.0"


# ==========================================================
# Database
# ==========================================================

SUPABASE_URL = ""

SUPABASE_KEY = ""


# ==========================================================
# Export Settings
# ==========================================================

DEFAULT_REPORT_NAME = "Retail_Analytics_Report"


# ==========================================================
# Database
# ==========================================================

ANALYSIS_TABLE = "analysis_history"