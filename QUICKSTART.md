# 🚀 Quick Start Guide

This is the fastest way to get the Public Procurement Transparency project up and running!

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies (1 minute)

```bash
# Navigate to project directory
cd DS_PROJECT

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt
```

### Step 2: Generate Sample Data (30 seconds)

```bash
python src/data/fetch_data.py
```

This creates sample Finnish procurement data in `data/raw/`.

### Step 3: Run Complete Pipeline (2 minutes)

```bash
python run_pipeline.py
```

This will:
- ✅ Clean and preprocess data
- ✅ Create analytical features
- ✅ Train anomaly detection models
- ✅ Generate risk scores
- ✅ Save results and models

### Step 4: Launch Dashboard (30 seconds)

```bash
streamlit run dashboard/app.py
```

Your browser will open to `http://localhost:8501` with an interactive dashboard!

## 📊 What You'll See

### Dashboard Features
- **KPI Metrics**: Total contracts, values, anomaly rates
- **Time Series**: Contract trends over time
- **Risk Analysis**: Risk distribution and high-risk contracts
- **Vendor Analysis**: Top vendors and concentration metrics
- **Interactive Filters**: Date range, category, risk level

### Sample Outputs

**High-Risk Contracts**: `data/processed/high_risk_contracts.csv`
- Contracts flagged as High or Critical risk
- Ready for audit review

**Anomaly Results**: `data/processed/anomaly_detection_results.csv`
- All contracts with risk scores
- Model predictions and explanations

## 🔬 Explore with Notebooks

```bash
jupyter notebook notebooks/01_EDA.ipynb
```

Interactive analysis with:
- Data quality assessment
- Distribution analysis
- Vendor concentration
- Temporal patterns
- Sustainability metrics

## 🧪 Run Tests

```bash
pytest tests/ -v
```

Validates all functionality is working correctly.

## 🎯 Next Steps

1. **Customize for Real Data**
   - Edit `src/data/fetch_data.py` to connect to actual data sources
   - Update API endpoints and credentials in `.env`

2. **Tune Detection**
   - Adjust contamination rate in `src/config.py`
   - Experiment with different features
   - Review and validate flagged anomalies

3. **Deploy Dashboard**
   - Deploy to Streamlit Cloud (free!)
   - Or use Docker for containerized deployment

## 💡 Common Commands

```bash
# Full pipeline
python run_pipeline.py

# Skip data fetching (use existing data)
python run_pipeline.py --skip-fetch

# Adjust contamination rate
python run_pipeline.py --contamination 0.1

# Launch dashboard
streamlit run dashboard/app.py

# Run notebooks
jupyter notebook

# Run tests
pytest tests/ -v
```

## 📁 Key Files

- `README.md` - Full project documentation
- `docs/GETTING_STARTED.md` - Detailed setup guide
- `docs/API.md` - API documentation
- `run_pipeline.py` - End-to-end pipeline
- `dashboard/app.py` - Streamlit dashboard
- `notebooks/` - Jupyter notebooks for analysis

## 🐛 Troubleshooting

**Dashboard shows "No data found"**
```bash
python run_pipeline.py
```

**Port 8501 already in use**
```bash
streamlit run dashboard/app.py --server.port 8502
```

**Module not found errors**
```bash
pip install -r requirements.txt
```

## 🌟 Features Highlight

✨ **Anomaly Detection**
- Isolation Forest for global outliers
- Local Outlier Factor for local anomalies
- SHAP explanations for interpretability

✨ **KPI Dashboard**
- Contract value trends
- Vendor concentration analysis
- Sustainability metrics
- Risk scoring and categorization

✨ **Data Quality**
- Automated cleaning and validation
- Feature engineering
- Reproducible pipeline

## 📞 Need Help?

- Check `docs/GETTING_STARTED.md` for detailed instructions
- Review `docs/API.md` for code documentation
- Open an issue on GitHub

---

**🎉 You're ready to detect procurement anomalies and promote transparency!**

Happy analyzing! 📊✨
