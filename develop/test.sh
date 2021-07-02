# Unittest and coverage using pytest
function unittest() {
    echo "==============================================="
    echo "Running Unittests with coverage"
    pytest --cov=ychaos --cov-report term-missing tests --durations=5
}

unittest