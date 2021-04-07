#!/bin/bash

function install_and_upgrade() {
    pip install -e ".[debug]" --upgrade
}

install_and_upgrade

# Install Git Hooks
pre-commit install -t pre-push