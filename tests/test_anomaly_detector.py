"""
Unit tests for anomaly detector module.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent / "src"))

from models.anomaly_detector import ProcurementAnomalyDetector


@pytest.fixture
def sample_data():
    """Create sample procurement data for testing."""
    np.random.seed(42)
    n = 100
    
    data = {
        'contract_id': [f'TEST-{i:04d}' for i in range(n)],
        'contract_value': np.random.lognormal(10, 1, n),
        'log_contract_value': np.random.normal(10, 1, n),
        'price_deviation_from_category': np.random.normal(0, 1, n),
        'vendor_contract_count': np.random.randint(1, 50, n),
        'vendor_authority_count': np.random.randint(1, 10, n),
        'days_to_award': np.random.randint(30, 120, n),
        'award_month': np.random.randint(1, 13, n),
        'award_quarter': np.random.randint(1, 5, n),
        'authority_vendor_count': np.random.randint(10, 100, n),
        'authority_contract_count': np.random.randint(50, 500, n)
    }
    
    return pd.DataFrame(data)


def test_detector_initialization():
    """Test detector initialization."""
    detector = ProcurementAnomalyDetector(contamination=0.05)
    assert detector.contamination == 0.05
    assert detector.iso_forest is None
    assert detector.lof is None


def test_prepare_features(sample_data):
    """Test feature preparation."""
    detector = ProcurementAnomalyDetector()
    X, feature_cols = detector.prepare_features(sample_data)
    
    assert X.shape[0] == len(sample_data)
    assert X.shape[1] > 0
    assert len(feature_cols) > 0
    assert not np.isnan(X).any()


def test_fit_isolation_forest(sample_data):
    """Test Isolation Forest training."""
    detector = ProcurementAnomalyDetector()
    X, _ = detector.prepare_features(sample_data)
    
    detector.fit_isolation_forest(X)
    
    assert detector.iso_forest is not None
    assert detector.scaler is not None


def test_predict_anomalies(sample_data):
    """Test anomaly prediction."""
    detector = ProcurementAnomalyDetector(contamination=0.1)
    X, _ = detector.prepare_features(sample_data)
    
    detector.fit_isolation_forest(X)
    detector.fit_lof(X)
    
    results = detector.predict_anomalies(sample_data)
    
    assert 'iso_anomaly' in results.columns
    assert 'lof_anomaly' in results.columns
    assert 'risk_score' in results.columns
    assert 'risk_category' in results.columns
    
    # Check anomaly rate is approximately as expected
    anomaly_rate = results['any_anomaly'].mean()
    assert 0.05 <= anomaly_rate <= 0.15  # Allow some variance


def test_risk_score_range(sample_data):
    """Test that risk scores are in valid range."""
    detector = ProcurementAnomalyDetector()
    X, _ = detector.prepare_features(sample_data)
    
    detector.fit_isolation_forest(X)
    detector.fit_lof(X)
    
    results = detector.predict_anomalies(sample_data)
    
    assert results['risk_score'].min() >= 0
    assert results['risk_score'].max() <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
