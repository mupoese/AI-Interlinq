#!/bin/bash
set -e

echo "🏁 Running AI-Interlinq performance benchmarks..."

# Create benchmarks directory
mkdir -p benchmarks/results

# Run comprehensive benchmarks
echo "📊 Running basic performance benchmark..."
ai-interlinq benchmark \
    --duration 60 \
    --agents 10 \
    --rate 1000 \
    --output benchmarks/results/basic_benchmark.json

echo "🚀 Running high-load benchmark..."
ai-interlinq benchmark \
    --duration 120 \
    --agents 50 \
    --rate 2000 \
    --output benchmarks/results/high_load_benchmark.json

echo "⚡ Running stress test..."
ai-interlinq benchmark \
    --duration 300 \
    --agents 100 \
    --rate 5000 \
    --output benchmarks/results/stress_test.json

echo "📋 Running comprehensive performance test..."
python examples/performance_benchmark.py > benchmarks/results/comprehensive_benchmark.txt

echo "✅ Benchmarks completed! Results saved in benchmarks/results/"
