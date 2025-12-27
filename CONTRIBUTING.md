# Contributing to Public Procurement Transparency

Thank you for considering contributing to this project! This document provides guidelines for contributing.

## How to Contribute

### Reporting Issues

- Use GitHub Issues to report bugs
- Include detailed description of the problem
- Provide steps to reproduce
- Include system information (OS, Python version)

### Suggesting Features

- Use GitHub Issues with "enhancement" label
- Clearly describe the feature and its benefits
- Provide use cases and examples

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest tests/`)
6. Update documentation as needed
7. Commit with clear messages (`git commit -m 'Add amazing feature'`)
8. Push to your fork (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone git@github.com:Venkatchavan/Procurement_Anomaly_Detection.git
cd Procurement_Anomaly_Detection

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"
```

## Code Style

- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and modular

### Code Formatting

```bash
# Format code with black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Check with flake8
flake8 src/ tests/
```

## Testing

- Write unit tests for new features
- Maintain test coverage above 80%
- Run tests before submitting PR

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Documentation

- Update README.md for user-facing changes
- Update API.md for API changes
- Add docstrings to new functions/classes
- Update GETTING_STARTED.md for setup changes

## Commit Messages

Use clear, descriptive commit messages:

```
Add feature: Brief description

Longer explanation if needed. Describe:
- What changed
- Why it changed
- Any breaking changes
```

## Code Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, maintainer will merge

## Community

- Be respectful and inclusive
- Follow our Code of Conduct
- Help others in discussions

## Questions?

Open an issue or reach out to maintainers.

Thank you for contributing! 🎉
