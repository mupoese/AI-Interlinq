#!/bin/bash
set -e

# Check if version is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 2.0.0"
    exit 1
fi

VERSION=$1

echo "🚀 Preparing release v$VERSION..."

# Update version in files
sed -i "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml
sed -i "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" ai_interlinq/__init__.py

# Run tests
echo "🧪 Running tests..."
pytest

# Run benchmarks
echo "📊 Running benchmarks..."
python examples/performance_benchmark.py

# Build package
echo "📦 Building package..."
python -m build

# Create git tag
git add -A
git commit -m "Release v$VERSION"
git tag -a "v$VERSION" -m "Release v$VERSION"

echo "✅ Release v$VERSION prepared!"
echo "📤 Run 'git push origin main --tags' to publish"
echo "📦 Run 'twine upload dist/*' to publish to PyPI"
