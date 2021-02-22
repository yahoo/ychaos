#!/bin/bash

# Format Codestyle to Black
function format_codestyle() {
    echo "==============================================="
    echo "Refactoring code to black"
    black .
}

# Sort Imports using isort
function sort_imports() {
    echo "==============================================="
    echo "Sorting imports"
    isort -m 3 --tc vzmi/ || { echo "Sorting imports failed" ; exit 1; }
    echo "Sorting imports complete"
}

# Style validation using Flake8
function flake8_validation() {
    echo "==============================================="
    echo "Running flake8 Style Check"
    flake8 vzmi/ychaos || { echo "flake8 Style Validation Failed" ; exit 1; }
    echo "flake8 Style Validation passing"
}

# Type Validation using mypy
function type_validation() {
    echo "================================================"
    echo "Running Type validation"
    mypy --ignore-missing-imports -p vzmi.ychaos || { echo "Type validation failed" ; exit 1; }
}

# Security Validation using Bandit
function security_validation() {
    echo "================================================"
    echo "Running Security Checks"
    bandit -r vzmi/ychaos -s B101 -q || { echo "Security validation failed" ; exit 1; }
    echo "No security vulnerabilities found"
}

# Unittest and coverage using green
function unittest() {
    echo "==============================================="
    echo "Running Unittests with coverage"
    pytest --cov=vzmi.ychaos --cov-report=html:artifacts/coverage --cov-report term-missing tests --cov-fail-under=70 --durations=5
    rm .coverage*
}

function autogen_cli_docs() {
    echo "==============================================="
    echo "Autogenerating CLI documentation"
    ychaos manual --file docs/cli/manual.md > /dev/null
    echo "Done"
}

format_codestyle
sort_imports

autogen_cli_docs

flake8_validation
type_validation
security_validation

unittest
