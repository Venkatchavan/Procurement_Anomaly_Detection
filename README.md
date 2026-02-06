# Public Procurement Transparency & Anomaly Detection

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)
![Status: Active](https://img.shields.io/badge/Status-Active-success)

**A Data-Driven Approach to Anti-Corruption and Sustainability in Public Procurement**

## 🎯 Project Overview

This project provides an end-to-end pipeline for analyzing public procurement data to promote transparency, detect anomalies, and support anti-corruption efforts. Using Finnish public procurement data as a reference implementation, the system delivers:

- **KPI Dashboards** for transparency and sustainability metrics
- **Anomaly Detection** using machine learning to flag irregular patterns
- **Explainability** features to support audits and decision-making
- **Reproducible Analysis** with modular code and clear documentation

## 🌟 Why This Matters

### EU Public Sector Context
- **Regulatory Compliance**: EU Directive [2014/24/EU](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32014L0024) mandates procurement transparency
- **ESG & Anti-Corruption**: Essential for compliance monitoring and risk assessment
- **Public Trust**: Increases accountability in government spending

### Key Use Cases
- Audit firms identifying high-risk contracts
- Public agencies monitoring procurement patterns
- Researchers studying corruption indicators
- Consulting firms assessing compliance

## 📊 Features

### 1. Interactive KPI Dashboard
- Contract value distributions and trends
- Vendor concentration analysis
- Sustainability indicators (green suppliers)
- Temporal patterns and seasonality

### 2. Anomaly Detection
- **Isolation Forest**: Detects unusual contract patterns
- **Local Outlier Factor (LOF)**: Identifies local anomalies
- Flags: overpricing, favoritism, irregular award patterns
- Risk scoring for contracts

### 3. Explainability
- SHAP values for model interpretability
- Rule-based explanations for anomalies
- Feature importance analysis
- Audit-ready reports

## 🏗️ Architecture

```
DS_PROJECT/
├── data/
│   ├── raw/                    # Original procurement data
│   └── processed/              # Cleaned and transformed data
├── notebooks/
│   ├── 01_EDA.ipynb           # Exploratory Data Analysis
│   └── 02_anomaly_detection.ipynb
├── src/
│   ├── data/
│   │   ├── fetch_data.py      # Data ingestion scripts
│   │   └── preprocess.py      # Data cleaning and preparation
│   ├── models/
│   │   ├── anomaly_detector.py # ML models for anomaly detection
│   │   └── explainer.py       # SHAP and explainability
│   └── visualization/
│       └── metrics.py         # KPI calculation functions
├── dbt_project/
│   └── models/
│       ├── staging/           # Raw data transformations
│       └── marts/             # Business logic models
├── dashboard/
│   └── app.py                 # Streamlit dashboard
├── tests/                     # Unit tests
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip or conda for package management
- (Optional) dbt-core for SQL transformations

### Installation

1. **Clone the repository**
```bash
git clone git@github.com:Venkatchavan/Procurement_Anomaly_Detection.git
cd Procurement_Anomaly_Detection
```

2. **Create a virtual environment**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up data directory**
```bash
# Sample data will be generated automatically
python src/data/fetch_data.py
```

### Quick Start

#### 1. Run Exploratory Data Analysis
```bash
jupyter notebook notebooks/01_EDA.ipynb
```

#### 2. Train Anomaly Detection Models
```bash
jupyter notebook notebooks/02_anomaly_detection.ipynb
```

#### 3. Launch Dashboard
```bash
streamlit run dashboard/app.py
```

The dashboard will open at `http://localhost:8501`

#### 4. (Optional) Run dbt transformations
```bash
cd dbt_project
dbt run
dbt test
```

## 📈 Data Sources

### Primary Dataset: Finnish Open Data
- **Source**: [avoindata.fi](https://avoindata.fi)
- **Content**: Public procurement contracts, invoices, vendor information
- **Fields**: 
  - Contract values and dates
  - Vendor details (name, ID, type)
  - Category/CPV codes
  - Sustainability labels (where available)

### Adaptable to Other EU Data
The pipeline is designed to work with:
- [TED (Tenders Electronic Daily)](https://ted.europa.eu/) - EU-wide procurement
- National procurement portals across EU member states
- Custom procurement datasets (see data schema documentation)

## 🔍 Anomaly Detection Methodology

### Features Used
- Contract value (normalized by category)
- Award frequency per vendor
- Time between tender and award
- Vendor diversity index
- Price deviation from category mean
- Contract amendment frequency

### Models
1. **Isolation Forest**
   - Good for global outliers
   - Contamination rate: 5% (configurable)

2. **Local Outlier Factor (LOF)**
   - Identifies local anomalies
   - K-neighbors: 20 (configurable)

### Evaluation Metrics
- Precision/Recall on labeled test set
- Anomaly score distribution
- Human expert validation (qualitative)

## 📊 Dashboard Screenshots

![Dashboard Overview](docs/screenshots/dashboard_overview.png)
*Main KPI dashboard with contract value trends*

![Anomaly Detection](docs/screenshots/anomaly_view.png)
*Anomaly detection results with risk scores*

![Explainability](docs/screenshots/shap_explanation.png)
*SHAP explanation for flagged contracts*

## 🧪 Testing

Run unit tests:
```bash
pytest tests/
```

Run specific test modules:
```bash
pytest tests/test_anomaly_detector.py -v
```

## 📝 Limitations

### Data Quality
- Relies on completeness and accuracy of source data
- Missing sustainability labels in many datasets
- Historical data may lack standardization

### Model Limitations
- Unsupervised models require manual threshold tuning
- False positives expected (5-10% typical)
- Domain expertise needed for validation
- Does not replace human audit processes

### Scope
- Focuses on statistical anomalies, not legal violations
- Requires domain knowledge for interpretation
- Best used as a screening tool, not definitive evidence

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Finnish Open Data Portal ([avoindata.fi](https://avoindata.fi))
- EU TED Platform ([ted.europa.eu](https://ted.europa.eu))
- Open source community for tools and libraries

## 📧 Contact
- **Issues**: [GitHub Issues](https://github.com/Venkatchavan/Procurement_Anomaly_Detection/issues)

## 🗺️ Roadmap

- [ ] Integration with EU TED API
- [ ] Network analysis of vendor relationships
- [ ] Time-series forecasting for budget planning
- [ ] Multi-language support (Finnish, Swedish, English)
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/Azure/GCP)
- [ ] Real-time monitoring capabilities

## 📚 Additional Resources

- [EU Procurement Directives](https://ec.europa.eu/growth/single-market/public-procurement_en)
- [OECD Anti-Corruption Guidelines](https://www.oecd.org/corruption/)
- [Transparency International](https://www.transparency.org/)
- [Open Contracting Partnership](https://www.open-contracting.org/)

---

**⭐ If you find this project useful, please consider giving it a star!**

*Built with ❤️ for transparency and accountability in public spending*
