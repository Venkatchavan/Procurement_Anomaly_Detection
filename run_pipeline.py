"""
End-to-end pipeline for procurement transparency analysis.
Runs the complete workflow from data fetching to anomaly detection.
"""

import sys
from pathlib import Path
import logging
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.data.fetch_data import ProcurementDataFetcher
from src.data.preprocess import ProcurementDataPreprocessor
from src.models.anomaly_detector import ProcurementAnomalyDetector
from src.config import (
    RAW_DATA_DIR, 
    PROCESSED_DATA_DIR, 
    MODELS_DIR, 
    LOGGING_CONFIG
)

# Setup logging
logging.basicConfig(
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_pipeline(
    n_records: int = 2000,
    contamination: float = 0.05,
    skip_fetch: bool = False
):
    """
    Run the complete procurement transparency pipeline.
    
    Args:
        n_records: Number of records to fetch/generate
        contamination: Anomaly detection contamination rate
        skip_fetch: Skip data fetching if data already exists
    """
    
    logger.info("="*70)
    logger.info("PROCUREMENT TRANSPARENCY PIPELINE")
    logger.info("="*70)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Step 1: Data Fetching
        if not skip_fetch:
            logger.info("\n" + "="*70)
            logger.info("STEP 1: DATA FETCHING")
            logger.info("="*70)
            
            fetcher = ProcurementDataFetcher(output_dir=str(RAW_DATA_DIR))
            df_raw = fetcher.fetch_from_avoindata(limit=n_records)
            raw_file = fetcher.save_data(df_raw, "procurement_raw.csv")
            
            logger.info(f"✓ Fetched {len(df_raw):,} records")
            logger.info(f"✓ Saved to {raw_file}")
        else:
            logger.info("\n" + "="*70)
            logger.info("STEP 1: SKIPPING DATA FETCH (using existing data)")
            logger.info("="*70)
        
        # Step 2: Data Preprocessing
        logger.info("\n" + "="*70)
        logger.info("STEP 2: DATA PREPROCESSING")
        logger.info("="*70)
        
        preprocessor = ProcurementDataPreprocessor(
            input_dir=str(RAW_DATA_DIR),
            output_dir=str(PROCESSED_DATA_DIR)
        )
        
        df_raw = preprocessor.load_raw_data("procurement_raw.csv")
        logger.info(f"Loaded {len(df_raw):,} raw records")
        
        df_clean = preprocessor.clean_data(df_raw)
        logger.info(f"✓ Cleaned data: {len(df_clean):,} records remaining")
        
        df_processed = preprocessor.create_features(df_clean)
        logger.info(f"✓ Created features: {len(df_processed.columns)} total columns")
        
        is_valid, issues = preprocessor.validate_data(df_processed)
        if not is_valid:
            logger.warning(f"Data validation issues: {issues}")
        else:
            logger.info("✓ Data validation passed")
        
        processed_file = preprocessor.save_processed_data(df_processed, "procurement_clean.csv")
        logger.info(f"✓ Saved to {processed_file}")
        
        # Generate report
        report = preprocessor.generate_data_report(df_processed)
        logger.info(f"✓ Total value: €{report['total_value']:,.2f}")
        logger.info(f"✓ Unique vendors: {report['unique_vendors']:,}")
        logger.info(f"✓ Sustainability rate: {report['sustainability_rate']:.2f}%")
        
        # Step 3: Anomaly Detection
        logger.info("\n" + "="*70)
        logger.info("STEP 3: ANOMALY DETECTION")
        logger.info("="*70)
        
        detector = ProcurementAnomalyDetector(contamination=contamination)
        
        X, feature_cols = detector.prepare_features(df_processed)
        logger.info(f"Prepared {X.shape[1]} features for {X.shape[0]} records")
        
        detector.fit_isolation_forest(X)
        logger.info("✓ Trained Isolation Forest")
        
        detector.fit_lof(X)
        logger.info("✓ Trained Local Outlier Factor")
        
        results = detector.predict_anomalies(df_processed)
        logger.info(f"✓ Detected {results['any_anomaly'].sum():,} anomalies")
        
        # Save results
        results_file = PROCESSED_DATA_DIR / "anomaly_detection_results.csv"
        results.to_csv(results_file, index=False)
        logger.info(f"✓ Saved results to {results_file}")
        
        # Save high-risk contracts
        high_risk = results[results['risk_category'].isin(['High', 'Critical'])]
        high_risk_file = PROCESSED_DATA_DIR / "high_risk_contracts.csv"
        high_risk.to_csv(high_risk_file, index=False)
        logger.info(f"✓ Saved {len(high_risk):,} high-risk contracts to {high_risk_file}")
        
        # Save models
        detector.save_model(str(MODELS_DIR))
        logger.info(f"✓ Saved models to {MODELS_DIR}")
        
        # Step 4: Summary Report
        logger.info("\n" + "="*70)
        logger.info("PIPELINE SUMMARY")
        logger.info("="*70)
        
        logger.info(f"Total records processed: {len(results):,}")
        logger.info(f"Total contract value: €{results['contract_value'].sum():,.2f}")
        logger.info(f"\nAnomaly Detection Results:")
        logger.info(f"  - Isolation Forest: {results['iso_anomaly'].sum():,} ({results['iso_anomaly'].mean()*100:.2f}%)")
        logger.info(f"  - LOF: {results['lof_anomaly'].sum():,} ({results['lof_anomaly'].mean()*100:.2f}%)")
        logger.info(f"  - Combined: {results['any_anomaly'].sum():,} ({results['any_anomaly'].mean()*100:.2f}%)")
        logger.info(f"  - High confidence: {results['both_anomaly'].sum():,} ({results['both_anomaly'].mean()*100:.2f}%)")
        
        logger.info(f"\nRisk Distribution:")
        for category in ['Low', 'Medium', 'High', 'Critical']:
            count = (results['risk_category'] == category).sum()
            pct = count / len(results) * 100
            logger.info(f"  - {category}: {count:,} ({pct:.2f}%)")
        
        logger.info(f"\nOutput Files:")
        logger.info(f"  - Raw data: {RAW_DATA_DIR / 'procurement_raw.csv'}")
        logger.info(f"  - Processed data: {processed_file}")
        logger.info(f"  - Anomaly results: {results_file}")
        logger.info(f"  - High-risk contracts: {high_risk_file}")
        logger.info(f"  - Models: {MODELS_DIR}")
        
        logger.info("\n" + "="*70)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("="*70)
        logger.info(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        logger.info("\nNext Steps:")
        logger.info("  1. Review high-risk contracts in: " + str(high_risk_file))
        logger.info("  2. Explore data with notebooks in: notebooks/")
        logger.info("  3. Launch dashboard: streamlit run dashboard/app.py")
        
        return results
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run procurement transparency analysis pipeline"
    )
    parser.add_argument(
        "--records",
        type=int,
        default=2000,
        help="Number of records to process (default: 2000)"
    )
    parser.add_argument(
        "--contamination",
        type=float,
        default=0.05,
        help="Anomaly contamination rate (default: 0.05)"
    )
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="Skip data fetching and use existing raw data"
    )
    
    args = parser.parse_args()
    
    run_pipeline(
        n_records=args.records,
        contamination=args.contamination,
        skip_fetch=args.skip_fetch
    )


if __name__ == "__main__":
    main()
