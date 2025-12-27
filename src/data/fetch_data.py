"""
Data fetching and ingestion module for procurement data.
Fetches data from Finnish open data portal (avoindata.fi) and other sources.
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcurementDataFetcher:
    """Fetch procurement data from various sources."""
    
    def __init__(self, output_dir: str = "../data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def fetch_from_avoindata(self, limit: int = 1000) -> pd.DataFrame:
        """
        Fetch data from Finnish open data portal.
        
        Args:
            limit: Maximum number of records to fetch
            
        Returns:
            DataFrame with procurement data
        """
        logger.info(f"Fetching up to {limit} records from avoindata.fi...")
        
        # Note: This is a placeholder. Actual API endpoint would be needed.
        # For demonstration, we'll generate sample data
        logger.warning("Using sample data generation - replace with actual API call")
        
        return self._generate_sample_data(limit)
    
    def _generate_sample_data(self, n_records: int = 1000) -> pd.DataFrame:
        """
        Generate realistic sample procurement data for testing.
        
        Args:
            n_records: Number of records to generate
            
        Returns:
            DataFrame with sample procurement data
        """
        logger.info(f"Generating {n_records} sample procurement records...")
        
        np.random.seed(42)
        
        # Sample vendors
        vendors = [
            "Finnish Construction Ltd", "Nordic IT Solutions", "Green Energy Finland",
            "Healthcare Services Oy", "Education Materials AB", "Transport Solutions Ltd",
            "Consulting Group Finland", "Security Services Nordic", "Catering Finland Oy",
            "Maintenance Services Ltd", "IT Infrastructure AB", "Legal Advisory Finland",
            "Engineering Solutions Oy", "Marketing Agency Nordic", "Cleaning Services Ltd"
        ]
        
        # Sample contracting authorities
        authorities = [
            "City of Helsinki", "City of Espoo", "City of Tampere", "City of Vantaa",
            "Ministry of Finance", "Ministry of Education", "Ministry of Health",
            "Finnish Transport Infrastructure Agency", "National Police Board"
        ]
        
        # CPV categories
        cpv_categories = {
            "45000000": "Construction work",
            "72000000": "IT services: consulting, software development",
            "90000000": "Sewage, refuse, cleaning services",
            "85000000": "Health and social work services",
            "79000000": "Business services: law, marketing, consulting",
            "80000000": "Education and training services",
            "71000000": "Architectural, engineering services",
            "60000000": "Transport services",
            "55000000": "Hotel, restaurant and retail trade services",
            "50000000": "Repair and maintenance services"
        }
        
        # Generate dates
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2024, 12, 31)
        date_range = (end_date - start_date).days
        
        publish_dates = [start_date + timedelta(days=np.random.randint(0, date_range)) 
                        for _ in range(n_records)]
        award_dates = [pd + timedelta(days=np.random.randint(30, 120)) 
                      for pd in publish_dates]
        
        # Generate contract values (log-normal distribution)
        base_values = np.random.lognormal(mean=11, sigma=1.5, size=n_records)
        
        # Generate data
        data = {
            'contract_id': [f"FI-{datetime.now().year}-{i:06d}" for i in range(1, n_records + 1)],
            'contract_title': [f"Procurement Contract {i}" for i in range(1, n_records + 1)],
            'contract_value': base_values,
            'publish_date': publish_dates,
            'award_date': award_dates,
            'vendor_name': np.random.choice(vendors, n_records),
            'vendor_id': [f"FI{np.random.randint(10000000, 99999999)}" for _ in range(n_records)],
            'contracting_authority': np.random.choice(authorities, n_records),
            'cpv_code': np.random.choice(list(cpv_categories.keys()), n_records),
            'procedure_type': np.random.choice(['Open', 'Restricted', 'Negotiated', 'Competitive dialogue'], 
                                              n_records, p=[0.5, 0.3, 0.15, 0.05]),
            'country_code': 'FI',
            'region': np.random.choice(['Uusimaa', 'Pirkanmaa', 'Varsinais-Suomi', 'Pohjois-Pohjanmaa'], 
                                      n_records)
        }
        
        df = pd.DataFrame(data)
        
        # Add CPV descriptions
        df['cpv_description'] = df['cpv_code'].map(cpv_categories)
        
        # Add sustainability labels (10% of contracts)
        sustainability_labels = [''] * n_records
        sustainable_idx = np.random.choice(n_records, int(n_records * 0.1), replace=False)
        for idx in sustainable_idx:
            sustainability_labels[idx] = np.random.choice(['green', 'eco', 'sustainable'])
        df['sustainability_label'] = sustainability_labels
        
        # Inject some anomalies for testing (5%)
        anomaly_idx = np.random.choice(n_records, int(n_records * 0.05), replace=False)
        for idx in anomaly_idx:
            # Overpricing
            if np.random.random() < 0.5:
                df.loc[idx, 'contract_value'] *= np.random.uniform(3, 10)
            # Rapid award
            else:
                df.loc[idx, 'award_date'] = df.loc[idx, 'publish_date'] + timedelta(days=np.random.randint(1, 10))
        
        logger.info(f"Generated {len(df)} sample records")
        return df
    
    def save_data(self, df: pd.DataFrame, filename: str = "procurement_raw.csv") -> Path:
        """
        Save fetched data to CSV.
        
        Args:
            df: DataFrame to save
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False)
        logger.info(f"Data saved to {output_path}")
        return output_path


def main():
    """Main execution function."""
    fetcher = ProcurementDataFetcher(output_dir="../data/raw")
    
    # Fetch data
    df = fetcher.fetch_from_avoindata(limit=2000)
    
    # Save raw data
    fetcher.save_data(df, "procurement_raw.csv")
    
    # Print summary
    print(f"\n{'='*60}")
    print("DATA FETCH SUMMARY")
    print(f"{'='*60}")
    print(f"Records fetched: {len(df):,}")
    print(f"Date range: {df['publish_date'].min()} to {df['publish_date'].max()}")
    print(f"Total value: €{df['contract_value'].sum():,.2f}")
    print(f"Unique vendors: {df['vendor_name'].nunique()}")
    print(f"Unique authorities: {df['contracting_authority'].nunique()}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
