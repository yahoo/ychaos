#!/bin/bash

# Format Codestyle to Black
function format_codestyle() {
    echo "==============================================="
    echo "Refactoring code to black"
    black .
}

# Sort Imports using isort
function fix_imports() {
    echo "=============================================="
    echo "Fixing absolute imports"
    find src -type f -name "*.py" | while read -r fname; do
        absolufy-imports "${fname}" --never
    done
    echo "Fixing absolute imports complete"

    echo "==============================================="
    echo "Sorting imports"
    isort -m 3 --tc src/ || { echo "Sorting imports failed" ; exit 1; }
    isort -m 3 --tc tests/ || { echo "Sorting imports failed" ; exit 1; }
    echo "Sorting imports complete"
}

# Style validation using Flake8
function flake8_validation() {
    echo "==============================================="
    echo "Running flake8 Style Check"
    flake8 src/ychaos || { echo "flake8 Style Validation Failed" ; exit 1; }
    echo "flake8 Style Validation passing"
}

function codespell_validation() {
    echo "==============================================="
    echo "Running codespell validation"
    codespell src tests develop docs || { echo "codespell Validation Failed" ; exit 1; }
    echo "codespell validation passing"
}

# Type Validation using mypy
function type_validation() {
    echo "================================================"
    echo "Running Type validation"
    mypy --ignore-missing-imports src/ychaos || { echo "Type validation failed" ; exit 1; }
}

# Security Validation using Bandit
function security_validation() {
    echo "================================================"
    echo "Running Security Checks"
    bandit -r src/ychaos -s B101 -q || { echo "Security validation failed" ; exit 1; }
    echo "No security vulnerabilities found"
}

function autogen_cli_docs() {
    echo "==============================================="
    echo "Autogenerating CLI documentation"
    ychaos manual --file docs/cli/manual.md > /dev/null
    echo "Done"
}

# For PyCharm activate virtual environment
if [ -d "venv/" ];
then
echo "==============================================="
echo "Activating Virtual Environment"
source venv/bin/activate
fi

format_codestyle
fix_imports

autogen_cli_docs

flake8_validation
codespell_validation
type_validation
security_validation
