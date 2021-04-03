#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

from json_schema_for_humans.generate import (
    GenerationConfiguration,
    generate_from_filename,
)

AUTOGEN_SCHEMA_JS_FILE = "docs/testplan/playground/schema.min.js"
SCHEMA_JSON_FILE = "vzmi/ychaos/testplan/resources/schema.json"

print("Generating schema.min.js for playground..")

with open(AUTOGEN_SCHEMA_JS_FILE, "w") as autogen_schema_js, open(
    SCHEMA_JSON_FILE, "r"
) as schema_json_file:
    autogen_schema_js.write(f"testplan_schema={schema_json_file.read()}")
    autogen_schema_js.write("\n")

print("Done..")

print("Auto Generating Schema Documentation...")
DOCS_FILE = "docs/testplan/schema/index.html"
generate_from_filename(
    SCHEMA_JSON_FILE, DOCS_FILE, config=GenerationConfiguration(minify=False)
)
print("Done..")
