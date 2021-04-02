#!/bin/bash

function serve_docs() {
    mkdocs serve
}

python3 screwdriver/autogen_docs.py
serve_docs