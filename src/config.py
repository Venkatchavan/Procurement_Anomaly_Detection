"""
Configuration settings for the procurement transparency project.
"""

from pathlib import Path
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Data source configuration
DATA_SOURCE_CONFIG = {
    "avoindata_url": os.getenv("DATA_SOURCE_URL", "https://avoindata.fi/api/"),
    "api_key": os.getenv("API_KEY", ""),
    "default_limit": 1000,
    "timeout": 30
}

# Model configuration
MODEL_CONFIG = {
    "isolation_forest": {
        "contamination": float(os.getenv("ANOMALY_CONTAMINATION", "0.05")),
        "n_estimators": 100,
        "max_samples": "auto",
        "random_state": 42,
        "n_jobs": -1
    },
    "lof": {
        "n_neighbors": int(os.getenv("LOF_NEIGHBORS", "20")),
        "contamination": float(os.getenv("ANOMALY_CONTAMINATION", "0.05")),
        "novelty": True,
        "n_jobs": -1
    },
    "risk_score_weights": {
        "iso_weight": 0.5,
        "lof_weight": 0.5
    },
    "risk_thresholds": {
        "low": 50,
        "medium": 75,
        "high": 90,
        "critical": 100
    }
}

# Feature configuration
FEATURE_CONFIG = {
    "numerical_features": [
        "log_contract_value",
        "price_deviation_from_category",
        "vendor_contract_count",
        "vendor_authority_count",
        "days_to_award",
        "authority_vendor_count",
        "authority_contract_count"
    ],
    "categorical_features": [
        "award_month",
        "award_quarter",
        "cpv_description",
        "procedure_type"
    ],
    "required_features": [
        "contract_id",
        "contract_value",
        "vendor_name",
        "contracting_authority",
        "award_date"
    ]
}

# Dashboard configuration
DASHBOARD_CONFIG = {
    "port": int(os.getenv("DASHBOARD_PORT", "8501")),
    "title": os.getenv("DASHBOARD_TITLE", "Public Procurement Transparency Dashboard"),
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Logging configuration
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.getenv("LOG_FILE", str(LOGS_DIR / "app.log"))
}

# Data validation rules
VALIDATION_RULES = {
    "contract_value": {
        "min": 0,
        "max": 1e9
    },
    "days_to_award": {
        "min": 0,
        "max": 365
    },
    "required_columns": [
        "contract_id",
        "contract_value",
        "vendor_name",
        "contracting_authority",
        "award_date"
    ]
}

# Database configuration (for dbt)
DATABASE_CONFIG = {
    "type": "duckdb",
    "path": os.getenv("DATABASE_URL", str(DATA_DIR / "procurement.duckdb"))
}


def get_config(section: str) -> Dict[str, Any]:
    """
    Get configuration for a specific section.
    
    Args:
        section: Configuration section name
        
    Returns:
        Dictionary with configuration
    """
    configs = {
        "data_source": DATA_SOURCE_CONFIG,
        "model": MODEL_CONFIG,
        "feature": FEATURE_CONFIG,
        "dashboard": DASHBOARD_CONFIG,
        "logging": LOGGING_CONFIG,
        "validation": VALIDATION_RULES,
        "database": DATABASE_CONFIG
    }
    
    return configs.get(section, {})


def validate_config() -> bool:
    """
    Validate configuration settings.
    
    Returns:
        True if configuration is valid
    """
    # Check contamination rate
    contamination = MODEL_CONFIG["isolation_forest"]["contamination"]
    if not 0 < contamination < 1:
        raise ValueError(f"Contamination must be between 0 and 1, got {contamination}")
    
    # Check LOF neighbors
    neighbors = MODEL_CONFIG["lof"]["n_neighbors"]
    if neighbors < 1:
        raise ValueError(f"LOF neighbors must be positive, got {neighbors}")
    
    # Check risk weights sum to 1
    weights = MODEL_CONFIG["risk_score_weights"]
    total_weight = weights["iso_weight"] + weights["lof_weight"]
    if not abs(total_weight - 1.0) < 1e-6:
        raise ValueError(f"Risk weights must sum to 1, got {total_weight}")
    
    return True


if __name__ == "__main__":
    # Test configuration
    print("Configuration Validation")
    print("=" * 60)
    
    try:
        validate_config()
        print("✓ Configuration valid")
        
        print(f"\nProject root: {PROJECT_ROOT}")
        print(f"Data directory: {DATA_DIR}")
        print(f"Models directory: {MODELS_DIR}")
        
        print(f"\nModel Configuration:")
        print(f"  Contamination: {MODEL_CONFIG['isolation_forest']['contamination']}")
        print(f"  LOF neighbors: {MODEL_CONFIG['lof']['n_neighbors']}")
        
        print(f"\nDashboard Configuration:")
        print(f"  Port: {DASHBOARD_CONFIG['port']}")
        print(f"  Title: {DASHBOARD_CONFIG['title']}")
        
    except Exception as e:
        print(f"✗ Configuration error: {e}")
