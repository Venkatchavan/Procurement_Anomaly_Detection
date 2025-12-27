"""
Unit tests for data preprocessing module.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent / "src"))

from data.preprocess import ProcurementDataPreprocessor


@pytest.fixture
def raw_data():
    """Create raw sample data for testing."""
    n = 50
    
    data = {
        'contract_id': [f'TEST-{i:04d}' for i in range(n)],
        'contract_title': [f'  Contract {i}  ' for i in range(n)],  # With whitespace
        'contract_value': np.random.lognormal(10, 1, n),
        'vendor_name': [f'  Vendor {i % 5}  ' for i in range(n)],
        'contracting_authority': [f'Authority {i % 3}' for i in range(n)],
        'award_date': [datetime.now() - timedelta(days=i*10) for i in range(n)],
        'publish_date': [datetime.now() - timedelta(days=i*10 + 60) for i in range(n)],
        'cpv_description': [f'Category {i % 3}' for i in range(n)],
        'sustainability_label': ['green' if i % 10 == 0 else '' for i in range(n)]
    }
    
    # Add some problematic data
    df = pd.DataFrame(data)
    df.loc[0, 'contract_value'] = -100  # Negative value
    df.loc[1, 'contract_id'] = None  # Missing ID
    df.loc[2, 'contract_value'] = 1e10  # Unrealistic value
    
    return df


def test_preprocessor_initialization():
    """Test preprocessor initialization."""
    preprocessor = ProcurementDataPreprocessor(
        input_dir="../data/raw",
        output_dir="../data/processed"
    )
    
    assert preprocessor.input_dir.name == "raw"
    assert preprocessor.output_dir.name == "processed"


def test_clean_data(raw_data):
    """Test data cleaning."""
    preprocessor = ProcurementDataPreprocessor()
    cleaned = preprocessor.clean_data(raw_data)
    
    # Check problematic records removed
    assert len(cleaned) < len(raw_data)
    
    # Check all values positive
    assert (cleaned['contract_value'] > 0).all()
    
    # Check no missing critical fields
    assert cleaned['contract_id'].notna().all()
    assert cleaned['contract_value'].notna().all()
    
    # Check text fields cleaned
    assert not cleaned['contract_title'].str.contains('  ').any()


def test_create_features(raw_data):
    """Test feature creation."""
    preprocessor = ProcurementDataPreprocessor()
    cleaned = preprocessor.clean_data(raw_data)
    enriched = preprocessor.create_features(cleaned)
    
    # Check new features exist
    assert 'award_year' in enriched.columns
    assert 'award_month' in enriched.columns
    assert 'days_to_award' in enriched.columns
    assert 'log_contract_value' in enriched.columns
    assert 'is_sustainable' in enriched.columns
    
    # Check days_to_award is non-negative
    assert (enriched['days_to_award'] >= 0).all()


def test_validate_data(raw_data):
    """Test data validation."""
    preprocessor = ProcurementDataPreprocessor()
    cleaned = preprocessor.clean_data(raw_data)
    enriched = preprocessor.create_features(cleaned)
    
    is_valid, issues = preprocessor.validate_data(enriched)
    
    assert isinstance(is_valid, bool)
    assert isinstance(issues, list)
    
    if is_valid:
        assert len(issues) == 0


def test_generate_data_report(raw_data):
    """Test report generation."""
    preprocessor = ProcurementDataPreprocessor()
    cleaned = preprocessor.clean_data(raw_data)
    enriched = preprocessor.create_features(cleaned)
    
    report = preprocessor.generate_data_report(enriched)
    
    assert 'total_records' in report
    assert 'total_value' in report
    assert 'unique_vendors' in report
    assert report['total_records'] == len(enriched)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
