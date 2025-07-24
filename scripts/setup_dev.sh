#!/bin/bash
set -e

echo "🚀 Setting up AI-Interlinq development environment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install development dependencies
pip install -r requirements-dev.txt

# Install package in development mode
pip install -e .

# Setup pre-commit hooks
pre-commit install

# Create necessary directories
mkdir -p logs
mkdir -p config
mkdir -p data
mkdir -p benchmarks

echo "✅ Development environment setup complete!"
echo "📝 Run 'source venv/bin/activate' to activate the environment"
