"""
Data preprocessing module for procurement data.
Cleans, validates, and prepares data for analysis and modeling.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Tuple, List, Optional
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcurementDataPreprocessor:
    """Preprocess and clean procurement data."""
    
    def __init__(self, input_dir: str = "../data/raw", output_dir: str = "../data/processed"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_raw_data(self, filename: str = "procurement_raw.csv") -> pd.DataFrame:
        """Load raw procurement data."""
        input_path = self.input_dir / filename
        logger.info(f"Loading data from {input_path}")
        
        df = pd.read_csv(input_path, parse_dates=['publish_date', 'award_date'])
        logger.info(f"Loaded {len(df):,} records")
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate procurement data.
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        logger.info("Starting data cleaning...")
        initial_count = len(df)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['contract_id'], keep='first')
        logger.info(f"Removed {initial_count - len(df)} duplicate records")
        
        # Remove records with missing critical fields
        critical_fields = ['contract_id', 'contract_value', 'vendor_name', 
                          'contracting_authority', 'award_date']
        df = df.dropna(subset=critical_fields)
        logger.info(f"Remaining records after null removal: {len(df):,}")
        
        # Clean contract values
        df = df[df['contract_value'] > 0]
        df = df[df['contract_value'] < 1e9]  # Remove unrealistic values
        logger.info(f"Remaining records after value filtering: {len(df):,}")
        
        # Clean text fields
        text_columns = ['contract_title', 'vendor_name', 'contracting_authority', 
                       'cpv_description']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].str.strip()
                df[col] = df[col].str.title()
        
        # Validate dates
        df = df[df['award_date'] >= df['publish_date']]
        df = df[df['award_date'] <= datetime.now()]
        logger.info(f"Remaining records after date validation: {len(df):,}")
        
        # Standardize vendor IDs
        if 'vendor_id' in df.columns:
            df['vendor_id'] = df['vendor_id'].str.upper().str.strip()
        
        # Create is_sustainable flag
        if 'sustainability_label' in df.columns:
            df['is_sustainable'] = df['sustainability_label'].isin(['green', 'eco', 'sustainable'])
        else:
            df['is_sustainable'] = False
        
        logger.info(f"Cleaning complete. Final record count: {len(df):,}")
        return df
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create additional features for analysis.
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            DataFrame with additional features
        """
        logger.info("Creating features...")
        
        # Temporal features
        df['award_year'] = df['award_date'].dt.year
        df['award_month'] = df['award_date'].dt.month
        df['award_quarter'] = df['award_date'].dt.quarter
        df['award_day_of_week'] = df['award_date'].dt.dayofweek
        
        # Time to award
        df['days_to_award'] = (df['award_date'] - df['publish_date']).dt.days
        
        # Value features
        df['log_contract_value'] = np.log10(df['contract_value'] + 1)
        
        # Category-based features
        category_stats = df.groupby('cpv_description')['contract_value'].agg(['mean', 'median', 'std'])
        category_stats.columns = ['category_mean_value', 'category_median_value', 'category_std_value']
        df = df.merge(category_stats, left_on='cpv_description', right_index=True, how='left')
        
        # Price deviation from category
        df['price_deviation_from_category'] = (
            (df['contract_value'] - df['category_mean_value']) / 
            (df['category_std_value'] + 1e-6)
        )
        
        # Vendor features
        vendor_stats = df.groupby('vendor_name').agg({
            'contract_value': ['sum', 'mean', 'count'],
            'contracting_authority': 'nunique'
        })
        vendor_stats.columns = ['vendor_total_value', 'vendor_avg_value', 
                                'vendor_contract_count', 'vendor_authority_count']
        df = df.merge(vendor_stats, left_on='vendor_name', right_index=True, how='left')
        
        # Authority features
        authority_stats = df.groupby('contracting_authority').agg({
            'contract_value': ['mean', 'count'],
            'vendor_name': 'nunique'
        })
        authority_stats.columns = ['authority_avg_value', 'authority_contract_count', 
                                   'authority_vendor_count']
        df = df.merge(authority_stats, left_on='contracting_authority', 
                     right_index=True, how='left')
        
        logger.info(f"Feature creation complete. Total columns: {len(df.columns)}")
        return df
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate processed data quality.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        logger.info("Validating data quality...")
        issues = []
        
        # Check for missing values in critical columns
        critical_cols = ['contract_id', 'contract_value', 'vendor_name', 
                        'contracting_authority', 'award_date']
        for col in critical_cols:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                issues.append(f"{col} has {missing_count} missing values")
        
        # Check value ranges
        if df['contract_value'].min() <= 0:
            issues.append("Contract values contain non-positive values")
        
        if df['days_to_award'].min() < 0:
            issues.append("Award dates before publish dates detected")
        
        # Check data types
        if not pd.api.types.is_datetime64_any_dtype(df['award_date']):
            issues.append("award_date is not datetime type")
        
        if not pd.api.types.is_numeric_dtype(df['contract_value']):
            issues.append("contract_value is not numeric type")
        
        is_valid = len(issues) == 0
        
        if is_valid:
            logger.info("✓ Data validation passed")
        else:
            logger.warning(f"✗ Data validation failed with {len(issues)} issues")
            for issue in issues:
                logger.warning(f"  - {issue}")
        
        return is_valid, issues
    
    def save_processed_data(self, df: pd.DataFrame, 
                           filename: str = "procurement_clean.csv") -> Path:
        """
        Save processed data.
        
        Args:
            df: Processed DataFrame
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False)
        logger.info(f"Processed data saved to {output_path}")
        return output_path
    
    def generate_data_report(self, df: pd.DataFrame) -> dict:
        """
        Generate summary statistics report.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        report = {
            'total_records': len(df),
            'total_value': df['contract_value'].sum(),
            'avg_value': df['contract_value'].mean(),
            'median_value': df['contract_value'].median(),
            'date_range': {
                'start': df['award_date'].min(),
                'end': df['award_date'].max()
            },
            'unique_vendors': df['vendor_name'].nunique(),
            'unique_authorities': df['contracting_authority'].nunique(),
            'unique_categories': df['cpv_description'].nunique(),
            'sustainable_contracts': df['is_sustainable'].sum(),
            'sustainability_rate': df['is_sustainable'].mean() * 100
        }
        return report


def main():
    """Main execution function."""
    preprocessor = ProcurementDataPreprocessor(
        input_dir="../data/raw",
        output_dir="../data/processed"
    )
    
    # Load raw data
    df = preprocessor.load_raw_data("procurement_raw.csv")
    
    # Clean data
    df = preprocessor.clean_data(df)
    
    # Create features
    df = preprocessor.create_features(df)
    
    # Validate
    is_valid, issues = preprocessor.validate_data(df)
    
    if is_valid:
        # Save processed data
        preprocessor.save_processed_data(df, "procurement_clean.csv")
        
        # Generate and print report
        report = preprocessor.generate_data_report(df)
        
        print(f"\n{'='*60}")
        print("DATA PREPROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total records: {report['total_records']:,}")
        print(f"Total value: €{report['total_value']:,.2f}")
        print(f"Average value: €{report['avg_value']:,.2f}")
        print(f"Median value: €{report['median_value']:,.2f}")
        print(f"Date range: {report['date_range']['start']} to {report['date_range']['end']}")
        print(f"Unique vendors: {report['unique_vendors']:,}")
        print(f"Unique authorities: {report['unique_authorities']:,}")
        print(f"Unique categories: {report['unique_categories']:,}")
        print(f"Sustainable contracts: {report['sustainable_contracts']:,} ({report['sustainability_rate']:.2f}%)")
        print(f"{'='*60}\n")
    else:
        logger.error("Data validation failed. Please review issues before proceeding.")


if __name__ == "__main__":
    main()
