#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

from os import environ
from json_schema_for_humans.generate import (
    GenerationConfiguration,
    generate_from_filename,
)
from ychaos.cli.main import YChaos

SCHEMA_JSON_FILE = "src/ychaos/testplan/resources/schema.json"

print("Auto Generating Schema Documentation...")
DOCS_FILE = "docs/testplan/schema/index.html"
generate_from_filename(
    SCHEMA_JSON_FILE, DOCS_FILE, config=GenerationConfiguration(minify=False)
)
print("Done..")

print("Setting the Column size")
environ["COLUMNS"] = "80"
print("Auto Generating CLI Documentation...")
CLI_DOC_OUT_FILE = "docs/cli/manual.md"
cli_command = "ychaos manual --file {}".format(CLI_DOC_OUT_FILE)
YChaos.main(cli_command.split()[1:])
print("Done..")
