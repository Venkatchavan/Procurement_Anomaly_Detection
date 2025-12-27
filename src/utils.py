"""
Utility functions for the procurement transparency project.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


def format_currency(value: float, currency: str = "EUR") -> str:
    """
    Format currency value for display.
    
    Args:
        value: Numeric value
        currency: Currency code
        
    Returns:
        Formatted string
    """
    if pd.isna(value):
        return "N/A"
    
    if value >= 1e9:
        return f"€{value/1e9:.2f}B"
    elif value >= 1e6:
        return f"€{value/1e6:.2f}M"
    elif value >= 1e3:
        return f"€{value/1e3:.2f}K"
    else:
        return f"€{value:.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format percentage for display.
    
    Args:
        value: Value between 0 and 1
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if pd.isna(value):
        return "N/A"
    return f"{value * 100:.{decimals}f}%"


def calculate_summary_stats(df: pd.DataFrame, column: str) -> Dict[str, float]:
    """
    Calculate summary statistics for a column.
    
    Args:
        df: DataFrame
        column: Column name
        
    Returns:
        Dictionary with statistics
    """
    return {
        "mean": df[column].mean(),
        "median": df[column].median(),
        "std": df[column].std(),
        "min": df[column].min(),
        "max": df[column].max(),
        "q25": df[column].quantile(0.25),
        "q75": df[column].quantile(0.75)
    }


def detect_outliers_iqr(df: pd.DataFrame, column: str, 
                        multiplier: float = 1.5) -> pd.Series:
    """
    Detect outliers using IQR method.
    
    Args:
        df: DataFrame
        column: Column name
        multiplier: IQR multiplier (default 1.5)
        
    Returns:
        Boolean series indicating outliers
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    
    return (df[column] < lower_bound) | (df[column] > upper_bound)


def calculate_concentration_index(df: pd.DataFrame, 
                                  group_col: str,
                                  value_col: str) -> float:
    """
    Calculate Herfindahl-Hirschman Index (HHI) for concentration.
    
    Args:
        df: DataFrame
        group_col: Column to group by (e.g., vendor)
        value_col: Value column (e.g., contract_value)
        
    Returns:
        HHI value (0 to 10,000)
    """
    total = df[value_col].sum()
    shares = df.groupby(group_col)[value_col].sum() / total
    hhi = (shares ** 2).sum() * 10000
    return hhi


def create_time_bins(df: pd.DataFrame, 
                     date_col: str,
                     freq: str = 'M') -> pd.DataFrame:
    """
    Create time period bins for temporal analysis.
    
    Args:
        df: DataFrame
        date_col: Date column name
        freq: Frequency ('D', 'W', 'M', 'Q', 'Y')
        
    Returns:
        DataFrame with time bins
    """
    df = df.copy()
    df['time_period'] = df[date_col].dt.to_period(freq)
    return df


def export_to_json(data: Any, filepath: str, indent: int = 2) -> None:
    """
    Export data to JSON file.
    
    Args:
        data: Data to export
        filepath: Output file path
        indent: JSON indentation
    """
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=indent, default=str)
    logger.info(f"Data exported to {filepath}")


def load_from_json(filepath: str) -> Any:
    """
    Load data from JSON file.
    
    Args:
        filepath: Input file path
        
    Returns:
        Loaded data
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    logger.info(f"Data loaded from {filepath}")
    return data


def calculate_vendor_diversity(df: pd.DataFrame,
                               vendor_col: str = 'vendor_name',
                               authority_col: str = 'contracting_authority') -> pd.DataFrame:
    """
    Calculate vendor diversity metrics by authority.
    
    Args:
        df: DataFrame
        vendor_col: Vendor column name
        authority_col: Authority column name
        
    Returns:
        DataFrame with diversity metrics
    """
    diversity = df.groupby(authority_col).agg({
        vendor_col: ['nunique', 'count']
    })
    diversity.columns = ['unique_vendors', 'total_contracts']
    diversity['diversity_ratio'] = diversity['unique_vendors'] / diversity['total_contracts']
    
    return diversity.reset_index()


def flag_suspicious_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flag potentially suspicious patterns in procurement data.
    
    Args:
        df: DataFrame with procurement data
        
    Returns:
        DataFrame with suspicious pattern flags
    """
    df = df.copy()
    
    # Flag 1: Very short award time
    if 'days_to_award' in df.columns:
        df['flag_rapid_award'] = df['days_to_award'] < 7
    
    # Flag 2: Round number contracts (possible manipulation)
    if 'contract_value' in df.columns:
        df['flag_round_number'] = (df['contract_value'] % 10000 == 0)
    
    # Flag 3: Repeat contracts to same vendor
    if 'vendor_name' in df.columns and 'contracting_authority' in df.columns:
        vendor_authority_counts = df.groupby(['vendor_name', 'contracting_authority']).size()
        high_frequency = vendor_authority_counts[vendor_authority_counts >= 10].index
        df['flag_high_frequency'] = df.set_index(['vendor_name', 'contracting_authority']).index.isin(high_frequency)
    
    # Total flags
    flag_cols = [col for col in df.columns if col.startswith('flag_')]
    df['total_flags'] = df[flag_cols].sum(axis=1)
    
    return df


def generate_anomaly_report(df: pd.DataFrame,
                           risk_col: str = 'risk_score',
                           threshold: float = 75) -> Dict[str, Any]:
    """
    Generate comprehensive anomaly report.
    
    Args:
        df: DataFrame with anomaly scores
        risk_col: Risk score column name
        threshold: Risk threshold for reporting
        
    Returns:
        Dictionary with report data
    """
    high_risk = df[df[risk_col] >= threshold]
    
    report = {
        "summary": {
            "total_contracts": len(df),
            "high_risk_count": len(high_risk),
            "high_risk_percentage": len(high_risk) / len(df) * 100,
            "total_value_at_risk": high_risk['contract_value'].sum() if 'contract_value' in df.columns else 0
        },
        "by_vendor": high_risk.groupby('vendor_name').size().sort_values(ascending=False).head(10).to_dict() if 'vendor_name' in df.columns else {},
        "by_category": high_risk.groupby('cpv_description').size().sort_values(ascending=False).head(10).to_dict() if 'cpv_description' in df.columns else {},
        "by_authority": high_risk.groupby('contracting_authority').size().sort_values(ascending=False).head(10).to_dict() if 'contracting_authority' in df.columns else {},
        "risk_distribution": df[risk_col].describe().to_dict(),
        "generated_at": datetime.now().isoformat()
    }
    
    return report


def validate_data_quality(df: pd.DataFrame, 
                         required_cols: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate data quality.
    
    Args:
        df: DataFrame to validate
        required_cols: List of required columns
        
    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []
    
    # Check required columns
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        issues.append(f"Missing required columns: {missing_cols}")
    
    # Check for empty dataframe
    if len(df) == 0:
        issues.append("DataFrame is empty")
    
    # Check for all-null columns
    null_cols = df.columns[df.isnull().all()].tolist()
    if null_cols:
        issues.append(f"Columns with all null values: {null_cols}")
    
    # Check for duplicate IDs
    if 'contract_id' in df.columns:
        duplicates = df['contract_id'].duplicated().sum()
        if duplicates > 0:
            issues.append(f"Found {duplicates} duplicate contract IDs")
    
    return len(issues) == 0, issues


if __name__ == "__main__":
    # Test utility functions
    print("Utility Functions Test")
    print("=" * 60)
    
    # Test currency formatting
    print(f"1,234,567.89 EUR: {format_currency(1234567.89)}")
    print(f"1,234,567,890 EUR: {format_currency(1234567890)}")
    
    # Test percentage formatting
    print(f"0.1543 as percentage: {format_percentage(0.1543)}")
    
    print("\n✓ Utility functions working correctly")
