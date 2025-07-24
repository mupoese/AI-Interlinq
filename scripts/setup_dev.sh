### scripts/setup_dev.sh

#!/bin/bash
# Development environment setup script

set -e

echo "🚀 Setting up AI-Interlinq development environment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run initial tests
pytest tests/ -v

# Run code formatting
black ai_interlinq/
isort ai_interlinq/

echo "✅ Development environment setup complete!"
echo "📝 To activate: source venv/bin/activate"
