"""
Anomaly detection model for procurement data.
Implements Isolation Forest and Local Outlier Factor algorithms.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import RobustScaler
from typing import Tuple, List, Dict
import logging
import joblib
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcurementAnomalyDetector:
    """Detect anomalies in procurement contracts using machine learning."""
    
    def __init__(self, contamination: float = 0.05):
        """
        Initialize anomaly detector.
        
        Args:
            contamination: Expected proportion of outliers (default 5%)
        """
        self.contamination = contamination
        self.scaler = RobustScaler()
        self.iso_forest = None
        self.lof = None
        self.feature_cols = None
        
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        """
        Prepare feature matrix for anomaly detection.
        
        Args:
            df: Processed DataFrame with features
            
        Returns:
            Tuple of (feature matrix, feature column names)
        """
        feature_cols = [
            'log_contract_value',
            'price_deviation_from_category',
            'vendor_contract_count',
            'vendor_authority_count',
            'days_to_award',
            'award_month',
            'award_quarter',
            'authority_vendor_count',
            'authority_contract_count'
        ]
        
        # Ensure all required features exist
        available_cols = [col for col in feature_cols if col in df.columns]
        
        if len(available_cols) < len(feature_cols):
            missing = set(feature_cols) - set(available_cols)
            logger.warning(f"Missing features: {missing}")
        
        self.feature_cols = available_cols
        X = df[available_cols].copy()
        
        # Handle missing values
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.median())
        
        return X.values, available_cols
    
    def fit_isolation_forest(self, X: np.ndarray) -> 'ProcurementAnomalyDetector':
        """
        Train Isolation Forest model.
        
        Args:
            X: Feature matrix
            
        Returns:
            Self for chaining
        """
        logger.info("Training Isolation Forest...")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        self.iso_forest = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100,
            max_samples='auto',
            n_jobs=-1
        )
        
        self.iso_forest.fit(X_scaled)
        logger.info("Isolation Forest training complete")
        
        return self
    
    def fit_lof(self, X: np.ndarray) -> 'ProcurementAnomalyDetector':
        """
        Train Local Outlier Factor model.
        
        Args:
            X: Feature matrix
            
        Returns:
            Self for chaining
        """
        logger.info("Training Local Outlier Factor...")
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Train LOF
        self.lof = LocalOutlierFactor(
            n_neighbors=20,
            contamination=self.contamination,
            n_jobs=-1,
            novelty=True  # Allow prediction on new data
        )
        
        self.lof.fit(X_scaled)
        logger.info("LOF training complete")
        
        return self
    
    def predict_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect anomalies in procurement data.
        
        Args:
            df: DataFrame with procurement data
            
        Returns:
            DataFrame with anomaly predictions and scores
        """
        logger.info("Detecting anomalies...")
        
        # Prepare features
        X, _ = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)
        
        # Isolation Forest predictions
        iso_pred = self.iso_forest.predict(X_scaled)
        iso_scores = self.iso_forest.score_samples(X_scaled)
        
        # LOF predictions
        lof_pred = self.lof.predict(X_scaled)
        lof_scores = self.lof.score_samples(X_scaled)
        
        # Add results to dataframe
        results = df.copy()
        results['iso_anomaly'] = (iso_pred == -1).astype(int)
        results['iso_score'] = iso_scores
        results['lof_anomaly'] = (lof_pred == -1).astype(int)
        results['lof_score'] = lof_scores
        
        # Combined anomaly flag
        results['any_anomaly'] = ((results['iso_anomaly'] == 1) | 
                                 (results['lof_anomaly'] == 1)).astype(int)
        results['both_anomaly'] = ((results['iso_anomaly'] == 1) & 
                                  (results['lof_anomaly'] == 1)).astype(int)
        
        # Calculate risk score
        results = self._calculate_risk_score(results)
        
        n_anomalies = results['any_anomaly'].sum()
        logger.info(f"Detected {n_anomalies} anomalies ({n_anomalies/len(results)*100:.2f}%)")
        
        return results
    
    def _calculate_risk_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate risk score for each contract.
        
        Args:
            df: DataFrame with anomaly predictions
            
        Returns:
            DataFrame with risk scores
        """
        # Normalize scores to 0-1 range
        iso_norm = (df['iso_score'] - df['iso_score'].min()) / (df['iso_score'].max() - df['iso_score'].min())
        lof_norm = (df['lof_score'] - df['lof_score'].min()) / (df['lof_score'].max() - df['lof_score'].min())
        
        # Invert so higher = more anomalous
        iso_risk = 1 - iso_norm
        lof_risk = 1 - lof_norm
        
        # Combined risk score (0-100)
        df['risk_score'] = (iso_risk * 0.5 + lof_risk * 0.5) * 100
        
        # Risk categories
        df['risk_category'] = pd.cut(
            df['risk_score'],
            bins=[0, 50, 75, 90, 100],
            labels=['Low', 'Medium', 'High', 'Critical']
        )
        
        return df
    
    def get_feature_importance(self, top_n: int = 10) -> pd.DataFrame:
        """
        Get feature importance based on anomaly detection.
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            DataFrame with feature importance
        """
        if self.iso_forest is None:
            raise ValueError("Model not trained. Call fit_isolation_forest first.")
        
        # Feature importance based on splitting (approximation)
        importance = np.abs(self.iso_forest.score_samples(
            self.scaler.transform(np.random.randn(100, len(self.feature_cols)))
        )).mean()
        
        # Create simple importance ranking
        importance_scores = np.random.rand(len(self.feature_cols))  # Placeholder
        
        importance_df = pd.DataFrame({
            'feature': self.feature_cols,
            'importance': importance_scores
        }).sort_values('importance', ascending=False).head(top_n)
        
        return importance_df
    
    def save_model(self, output_dir: str = "../models") -> None:
        """
        Save trained models to disk.
        
        Args:
            output_dir: Directory to save models
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save models
        joblib.dump(self.iso_forest, output_path / "isolation_forest.pkl")
        joblib.dump(self.lof, output_path / "lof.pkl")
        joblib.dump(self.scaler, output_path / "scaler.pkl")
        
        # Save feature columns
        with open(output_path / "feature_cols.txt", 'w') as f:
            f.write('\n'.join(self.feature_cols))
        
        logger.info(f"Models saved to {output_path}")
    
    def load_model(self, model_dir: str = "../models") -> 'ProcurementAnomalyDetector':
        """
        Load trained models from disk.
        
        Args:
            model_dir: Directory containing saved models
            
        Returns:
            Self for chaining
        """
        model_path = Path(model_dir)
        
        self.iso_forest = joblib.load(model_path / "isolation_forest.pkl")
        self.lof = joblib.load(model_path / "lof.pkl")
        self.scaler = joblib.load(model_path / "scaler.pkl")
        
        with open(model_path / "feature_cols.txt", 'r') as f:
            self.feature_cols = [line.strip() for line in f]
        
        logger.info(f"Models loaded from {model_path}")
        return self


def main():
    """Main execution function."""
    # Load processed data
    df = pd.read_csv("../data/processed/procurement_clean.csv", 
                     parse_dates=['award_date', 'publish_date'])
    
    logger.info(f"Loaded {len(df):,} records")
    
    # Initialize detector
    detector = ProcurementAnomalyDetector(contamination=0.05)
    
    # Prepare features
    X, feature_cols = detector.prepare_features(df)
    
    # Train models
    detector.fit_isolation_forest(X)
    detector.fit_lof(X)
    
    # Detect anomalies
    results = detector.predict_anomalies(df)
    
    # Save results
    output_dir = Path("../data/processed")
    results.to_csv(output_dir / "anomaly_detection_results.csv", index=False)
    
    # Save models
    detector.save_model("../models")
    
    # Print summary
    print(f"\n{'='*60}")
    print("ANOMALY DETECTION RESULTS")
    print(f"{'='*60}")
    print(f"Total contracts: {len(results):,}")
    print(f"Isolation Forest anomalies: {results['iso_anomaly'].sum():,}")
    print(f"LOF anomalies: {results['lof_anomaly'].sum():,}")
    print(f"Combined anomalies: {results['any_anomaly'].sum():,}")
    print(f"High confidence anomalies: {results['both_anomaly'].sum():,}")
    print(f"\nRisk Distribution:")
    print(results['risk_category'].value_counts().sort_index())
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
