# Getting Started Guide

This guide will help you set up and run the Public Procurement Transparency project.

## Prerequisites

- Python 3.9 or higher
- pip or conda package manager
- Git (for version control)
- (Optional) PostgreSQL or DuckDB for dbt transformations

## Installation Steps

### 1. Clone the Repository

```bash
git clone git@github.com:Venkatchavan/Procurement_Anomaly_Detection.git
cd Procurement_Anomaly_Detection
```

### 2. Create Virtual Environment

**Using venv:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Unix/MacOS
source venv/bin/activate
```

**Using conda:**
```bash
conda create -n procurement python=3.9
conda activate procurement
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# (Use your preferred text editor)
```

## Quick Start

### Generate Sample Data

```bash
python src/data/fetch_data.py
```

This will create sample procurement data in `data/raw/procurement_raw.csv`.

### Preprocess Data

```bash
python src/data/preprocess.py
```

This will clean and prepare the data, saving it to `data/processed/procurement_clean.csv`.

### Run Anomaly Detection

```bash
python src/models/anomaly_detector.py
```

This will detect anomalies and save results to `data/processed/anomaly_detection_results.csv`.

### Launch Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard will open in your browser at `http://localhost:8501`.

## Jupyter Notebooks

### Exploratory Data Analysis

```bash
jupyter notebook notebooks/01_EDA.ipynb
```

This notebook provides comprehensive data exploration and visualization.

### Anomaly Detection Analysis

```bash
jupyter notebook notebooks/02_anomaly_detection.ipynb
```

This notebook demonstrates the anomaly detection pipeline with SHAP explanations.

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_anomaly_detector.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## dbt Transformations (Optional)

If you want to use dbt for SQL-based transformations:

### 1. Install dbt

```bash
pip install dbt-core dbt-duckdb
```

### 2. Configure dbt Profile

Edit `dbt_project/profiles.yml` with your database connection details.

### 3. Run dbt Models

```bash
cd dbt_project
dbt run
dbt test
```

## Project Workflow

### End-to-End Pipeline

```bash
# 1. Fetch data
python src/data/fetch_data.py

# 2. Preprocess
python src/data/preprocess.py

# 3. Detect anomalies
python src/models/anomaly_detector.py

# 4. Launch dashboard
streamlit run dashboard/app.py
```

### Using Notebooks for Analysis

1. Start with `01_EDA.ipynb` to understand the data
2. Run `02_anomaly_detection.ipynb` for detailed anomaly analysis
3. Use dashboard for interactive exploration

## Customization

### Adding New Data Sources

Edit `src/data/fetch_data.py` to add new data fetching logic:

```python
def fetch_from_custom_source(self):
    # Your custom data fetching logic
    pass
```

### Tuning Anomaly Detection

Modify contamination rate and other parameters in `src/models/anomaly_detector.py`:

```python
detector = ProcurementAnomalyDetector(contamination=0.05)
```

### Customizing Dashboard

Edit `dashboard/app.py` to add new visualizations or modify layout.

## Troubleshooting

### Common Issues

**Issue: ModuleNotFoundError**
```bash
# Solution: Install missing packages
pip install -r requirements.txt
```

**Issue: Data file not found**
```bash
# Solution: Generate sample data first
python src/data/fetch_data.py
```

**Issue: Streamlit port already in use**
```bash
# Solution: Use different port
streamlit run dashboard/app.py --server.port 8502
```

### Getting Help

- Check [GitHub Issues](https://github.com/Venkatchavan/Procurement_Anomaly_Detection/issues)
- Review documentation in `docs/`
- Contact project maintainer

## Next Steps

1. **Explore the Data**: Run the EDA notebook to understand your data
2. **Tune Models**: Experiment with different contamination rates
3. **Add Features**: Create domain-specific features for better detection
4. **Integrate Real Data**: Replace sample data with actual procurement data
5. **Deploy**: Consider deploying the dashboard to cloud platforms

## Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [scikit-learn Anomaly Detection](https://scikit-learn.org/stable/modules/outlier_detection.html)
- [SHAP Documentation](https://shap.readthedocs.io/)
- [dbt Documentation](https://docs.getdbt.com/)

---

For more detailed information, see the main [README.md](../README.md).
