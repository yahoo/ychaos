#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

AUTOGEN_SCHEMA_JS_FILE = "docs/testplan/playground/schema.min.js"
SCHEMA_JSON_FILE = "vzmi/ychaos/testplan/resources/schema.json"

print("Generating schema.min.js for playground..")

with open(AUTOGEN_SCHEMA_JS_FILE, "w") as autogen_schema_js, open(SCHEMA_JSON_FILE, "r") as schema_json_file:
    autogen_schema_js.write(f"testplan_schema={schema_json_file.read()}")
    autogen_schema_js.write("\n")

print("Done..")
