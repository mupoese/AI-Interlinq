### scripts/run_tests.sh

#!/bin/bash
# Test execution script

set -e

echo "🧪 Running AI-Interlinq tests..."

# Run tests with coverage
pytest tests/ \
    --cov=ai_interlinq \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-fail-under=80 \
    -v

echo "✅ Tests completed!"
echo "📊 Coverage report: htmlcov/index.html"
