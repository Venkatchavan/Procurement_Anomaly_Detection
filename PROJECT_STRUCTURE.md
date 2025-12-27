# Project Structure

```
DS_PROJECT/
│
├── 📄 README.md                          # Main project documentation
├── 📄 QUICKSTART.md                      # Quick setup guide
├── 📄 CONTRIBUTING.md                    # Contribution guidelines
├── 📄 LICENSE                            # MIT License
├── 📄 requirements.txt                   # Python dependencies
├── 📄 setup.py                           # Package setup
├── 📄 .gitignore                         # Git ignore rules
├── 📄 .env.example                       # Environment variables example
├── 📄 Makefile                           # Build automation
├── 📄 run_pipeline.py                    # End-to-end pipeline script
│
├── 📁 data/                              # Data directory
│   ├── raw/                              # Raw data files
│   │   └── .gitkeep
│   └── processed/                        # Cleaned/processed data
│       └── .gitkeep
│
├── 📁 notebooks/                         # Jupyter notebooks
│   ├── 01_EDA.ipynb                     # Exploratory Data Analysis
│   └── 02_anomaly_detection.ipynb       # Anomaly Detection Analysis
│
├── 📁 src/                               # Source code
│   ├── __init__.py
│   ├── config.py                        # Configuration settings
│   ├── utils.py                         # Utility functions
│   │
│   ├── data/                            # Data processing modules
│   │   ├── __init__.py
│   │   ├── fetch_data.py               # Data fetching/generation
│   │   └── preprocess.py               # Data cleaning & feature engineering
│   │
│   ├── models/                          # ML models
│   │   ├── __init__.py
│   │   └── anomaly_detector.py         # Anomaly detection models
│   │
│   └── visualization/                   # Visualization utilities
│       └── __init__.py
│
├── 📁 dashboard/                         # Streamlit dashboard
│   └── app.py                           # Main dashboard application
│
├── 📁 dbt_project/                       # dbt SQL transformations
│   ├── dbt_project.yml                  # dbt configuration
│   ├── profiles.yml                     # Database profiles
│   │
│   └── models/                          # dbt models
│       ├── staging/                     # Staging layer
│       │   ├── schema.yml
│       │   ├── stg_procurement_contracts.sql
│       │   └── stg_vendors.sql
│       │
│       └── marts/                       # Business logic layer
│           ├── vendor_metrics.sql
│           └── temporal_metrics.sql
│
├── 📁 tests/                             # Unit tests
│   ├── test_anomaly_detector.py
│   └── test_preprocess.py
│
└── 📁 docs/                              # Documentation
    ├── screenshots/                      # Dashboard screenshots
    ├── GETTING_STARTED.md               # Detailed setup guide
    └── API.md                           # API documentation
```

## 📂 Directory Purposes

### `/data/`
- **raw/**: Original/fetched procurement data
- **processed/**: Cleaned data ready for analysis

### `/notebooks/`
- Interactive Jupyter notebooks for exploration and analysis
- Self-contained with visualizations and explanations

### `/src/`
- Modular Python source code
- **data/**: Data ingestion and preprocessing
- **models/**: Machine learning models
- **visualization/**: Plotting and dashboard utilities

### `/dashboard/`
- Streamlit web application
- Interactive KPI dashboard with filters

### `/dbt_project/`
- SQL-based data transformations
- **staging/**: Raw data cleaning
- **marts/**: Business metrics and aggregations

### `/tests/`
- Unit tests for all modules
- Ensures code quality and reliability

### `/docs/`
- Comprehensive documentation
- Setup guides and API references

## 🔑 Key Files

| File | Purpose |
|------|---------|
| `run_pipeline.py` | Execute complete analysis pipeline |
| `requirements.txt` | All Python dependencies |
| `dashboard/app.py` | Interactive Streamlit dashboard |
| `src/config.py` | Centralized configuration |
| `notebooks/01_EDA.ipynb` | Exploratory data analysis |
| `notebooks/02_anomaly_detection.ipynb` | Anomaly detection analysis |

## 🎯 Workflow

1. **Data Fetching** → `src/data/fetch_data.py`
2. **Preprocessing** → `src/data/preprocess.py`
3. **Feature Engineering** → (included in preprocessing)
4. **Anomaly Detection** → `src/models/anomaly_detector.py`
5. **Visualization** → `dashboard/app.py` or notebooks
6. **SQL Transformations** (optional) → `dbt_project/`

## 📊 Data Flow

```
Raw Data (CSV/API)
    ↓
fetch_data.py
    ↓
data/raw/procurement_raw.csv
    ↓
preprocess.py
    ↓
data/processed/procurement_clean.csv
    ↓
anomaly_detector.py
    ↓
data/processed/anomaly_detection_results.csv
    ↓
Dashboard / Notebooks
```

## 🚀 Getting Started

See [QUICKSTART.md](QUICKSTART.md) for immediate setup, or [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) for detailed instructions.

## 📝 Generated Files (not in repo)

After running the pipeline, these files will be created:

```
data/
├── raw/
│   └── procurement_raw.csv              # Sample data
├── processed/
│   ├── procurement_clean.csv            # Cleaned data
│   ├── anomaly_detection_results.csv    # All results
│   └── high_risk_contracts.csv          # High-risk subset
│
models/
├── isolation_forest.pkl                 # Trained IF model
├── lof.pkl                              # Trained LOF model
├── scaler.pkl                           # Feature scaler
└── feature_cols.txt                     # Feature names
│
logs/
└── app.log                              # Application logs
```

## 🔧 Configuration Files

- `.env` - Environment variables (create from `.env.example`)
- `src/config.py` - Python configuration
- `dbt_project/profiles.yml` - dbt database connections

---

**Built with ❤️ for transparency in public procurement**
