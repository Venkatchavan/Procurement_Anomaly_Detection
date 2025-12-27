# API Documentation

## Data Fetching Module

### `ProcurementDataFetcher`

Main class for fetching procurement data from various sources.

```python
from src.data.fetch_data import ProcurementDataFetcher

fetcher = ProcurementDataFetcher(output_dir="../data/raw")
df = fetcher.fetch_from_avoindata(limit=1000)
fetcher.save_data(df, "procurement_raw.csv")
```

#### Methods

**`__init__(output_dir: str = "../data/raw")`**
- Initialize fetcher with output directory
- Creates directory if it doesn't exist

**`fetch_from_avoindata(limit: int = 1000) -> pd.DataFrame`**
- Fetch data from Finnish open data portal
- Args:
  - `limit`: Maximum number of records
- Returns: DataFrame with procurement data

**`save_data(df: pd.DataFrame, filename: str) -> Path`**
- Save DataFrame to CSV
- Args:
  - `df`: DataFrame to save
  - `filename`: Output filename
- Returns: Path to saved file

## Preprocessing Module

### `ProcurementDataPreprocessor`

Class for cleaning and preparing procurement data.

```python
from src.data.preprocess import ProcurementDataPreprocessor

preprocessor = ProcurementDataPreprocessor(
    input_dir="../data/raw",
    output_dir="../data/processed"
)

df = preprocessor.load_raw_data("procurement_raw.csv")
df = preprocessor.clean_data(df)
df = preprocessor.create_features(df)
preprocessor.save_processed_data(df, "procurement_clean.csv")
```

#### Methods

**`clean_data(df: pd.DataFrame) -> pd.DataFrame`**
- Remove duplicates, invalid values, clean text
- Validates dates and standardizes formats
- Returns: Cleaned DataFrame

**`create_features(df: pd.DataFrame) -> pd.DataFrame`**
- Creates temporal, statistical, and aggregated features
- Adds vendor and category statistics
- Returns: DataFrame with additional features

**`validate_data(df: pd.DataFrame) -> Tuple[bool, List[str]]`**
- Validates data quality
- Returns: (is_valid, list of issues)

**`generate_data_report(df: pd.DataFrame) -> dict`**
- Generates summary statistics
- Returns: Dictionary with key metrics

## Anomaly Detection Module

### `ProcurementAnomalyDetector`

Main class for detecting procurement anomalies using machine learning.

```python
from src.models.anomaly_detector import ProcurementAnomalyDetector

detector = ProcurementAnomalyDetector(contamination=0.05)

# Prepare and train
X, feature_cols = detector.prepare_features(df)
detector.fit_isolation_forest(X)
detector.fit_lof(X)

# Predict
results = detector.predict_anomalies(df)

# Save model
detector.save_model("../models")
```

#### Methods

**`__init__(contamination: float = 0.05)`**
- Initialize detector
- Args:
  - `contamination`: Expected proportion of outliers (default 5%)

**`prepare_features(df: pd.DataFrame) -> Tuple[np.ndarray, List[str]]`**
- Extracts and prepares feature matrix
- Handles missing values
- Returns: (feature matrix, feature names)

**`fit_isolation_forest(X: np.ndarray) -> ProcurementAnomalyDetector`**
- Train Isolation Forest model
- Uses RobustScaler for feature scaling
- Returns: Self (for method chaining)

**`fit_lof(X: np.ndarray) -> ProcurementAnomalyDetector`**
- Train Local Outlier Factor model
- Uses novelty detection mode
- Returns: Self (for method chaining)

**`predict_anomalies(df: pd.DataFrame) -> pd.DataFrame`**
- Detect anomalies in procurement data
- Adds columns: `iso_anomaly`, `lof_anomaly`, `risk_score`, `risk_category`
- Returns: DataFrame with predictions

**`save_model(output_dir: str) -> None`**
- Saves trained models to disk
- Saves: Isolation Forest, LOF, scaler, feature names

**`load_model(model_dir: str) -> ProcurementAnomalyDetector`**
- Loads trained models from disk
- Returns: Self with loaded models

## Dashboard

### Running the Dashboard

```bash
streamlit run dashboard/app.py
```

### Key Functions

**`load_data() -> pd.DataFrame`**
- Loads processed procurement data
- Cached for performance

**`generate_sample_data(n: int) -> pd.DataFrame`**
- Generates sample data if real data not available

### Dashboard Components

1. **Filters Sidebar**
   - Date range filter
   - Category filter
   - Risk level filter
   - Anomaly toggle

2. **KPI Section**
   - Total contracts
   - Total value
   - Anomaly rate
   - Sustainability rate
   - Unique vendors

3. **Visualizations**
   - Time series trends
   - Risk distribution
   - Vendor analysis
   - Category distribution
   - Anomaly scatter plot

4. **High-Risk Contracts Table**
   - Sortable table
   - Export to CSV

## Data Schema

### Raw Data Schema

```python
{
    'contract_id': str,          # Unique identifier
    'contract_title': str,       # Contract title
    'contract_value': float,     # Value in EUR
    'publish_date': datetime,    # Publication date
    'award_date': datetime,      # Award date
    'vendor_name': str,          # Vendor name
    'vendor_id': str,            # Vendor ID
    'contracting_authority': str, # Authority name
    'cpv_code': str,             # CPV code
    'cpv_description': str,      # Category description
    'procedure_type': str,       # Procurement procedure
    'country_code': str,         # Country code
    'region': str,               # Region
    'sustainability_label': str  # Sustainability indicator
}
```

### Processed Data Schema

Includes all raw fields plus:

```python
{
    'award_year': int,
    'award_month': int,
    'award_quarter': int,
    'days_to_award': int,
    'log_contract_value': float,
    'price_deviation_from_category': float,
    'vendor_contract_count': int,
    'vendor_total_value': float,
    'vendor_authority_count': int,
    'authority_vendor_count': int,
    'is_sustainable': bool
}
```

### Anomaly Detection Results Schema

Includes all processed fields plus:

```python
{
    'iso_anomaly': int,          # 1 if anomaly, 0 if normal
    'iso_score': float,          # Isolation Forest score
    'lof_anomaly': int,          # 1 if anomaly, 0 if normal
    'lof_score': float,          # LOF score
    'any_anomaly': int,          # 1 if flagged by any model
    'both_anomaly': int,         # 1 if flagged by both models
    'risk_score': float,         # Combined risk score (0-100)
    'risk_category': str         # Low/Medium/High/Critical
}
```

## Configuration

### Environment Variables

```bash
# Data source
DATA_SOURCE_URL=https://avoindata.fi/api/
API_KEY=your_api_key

# Model parameters
ANOMALY_CONTAMINATION=0.05
LOF_NEIGHBORS=20

# Dashboard
DASHBOARD_PORT=8501
```

### Model Hyperparameters

**Isolation Forest:**
- `n_estimators`: 100 (number of trees)
- `max_samples`: 'auto'
- `contamination`: 0.05 (5% expected outliers)
- `random_state`: 42

**Local Outlier Factor:**
- `n_neighbors`: 20
- `contamination`: 0.05
- `novelty`: True

## Error Handling

### Common Exceptions

**`FileNotFoundError`**
- Raised when data files not found
- Solution: Generate data using fetch_data.py

**`ValueError`**
- Raised for invalid data or parameters
- Check data schema and parameter ranges

**`KeyError`**
- Raised when expected columns missing
- Ensure preprocessing completed successfully

## Performance Tips

1. **Large Datasets**: Use sampling for initial exploration
2. **Memory**: Process data in chunks if memory limited
3. **Speed**: Use `n_jobs=-1` for parallel processing
4. **Caching**: Dashboard uses `@st.cache_data` for performance

## Version Compatibility

- Python: 3.9+
- pandas: 1.5+
- scikit-learn: 1.2+
- streamlit: 1.22+

---

For examples and tutorials, see [GETTING_STARTED.md](GETTING_STARTED.md).
