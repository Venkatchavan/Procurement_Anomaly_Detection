# Makefile for Procurement Transparency Project

.PHONY: help install data preprocess detect dashboard notebook test clean all

help:
	@echo "Procurement Transparency Project - Available Commands"
	@echo "======================================================"
	@echo "make install      - Install project dependencies"
	@echo "make data         - Fetch/generate sample data"
	@echo "make preprocess   - Preprocess and clean data"
	@echo "make detect       - Run anomaly detection"
	@echo "make dashboard    - Launch Streamlit dashboard"
	@echo "make notebook     - Start Jupyter notebook server"
	@echo "make test         - Run unit tests"
	@echo "make clean        - Clean generated files"
	@echo "make all          - Run complete pipeline"
	@echo ""
	@echo "Quick start: make install && make all && make dashboard"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

data:
	@echo "Fetching data..."
	python src/data/fetch_data.py

preprocess:
	@echo "Preprocessing data..."
	python src/data/preprocess.py

detect:
	@echo "Running anomaly detection..."
	python src/models/anomaly_detector.py

dashboard:
	@echo "Launching dashboard..."
	streamlit run dashboard/app.py

notebook:
	@echo "Starting Jupyter notebook..."
	jupyter notebook

test:
	@echo "Running tests..."
	pytest tests/ -v

clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

all:
	@echo "Running complete pipeline..."
	python run_pipeline.py
