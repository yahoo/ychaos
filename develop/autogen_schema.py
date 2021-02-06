import json
from pkg_resources import resource_filename

from vzmi.ychaos.testplan.schema import TestPlanSchema

from json_schema_for_humans.generate import (
    GenerationConfiguration,
    generate_from_filename,
)

print("Auto Generating Schema...")

PKG_RESOURCES = "vzmi.ychaos.testplan.resources"
AUTOGEN_SCHEMA_FILE = str(resource_filename(PKG_RESOURCES, "schema.json"))
DOCS_FILE = "docs/testplan/schema/index.html"

with open(AUTOGEN_SCHEMA_FILE, "w") as autoGenSchema:
    json.dump(TestPlanSchema.schema(), autoGenSchema, indent=4)
    autoGenSchema.write("\n")

print("Done..")

print("Auto Generating Schema Documentation...")
generate_from_filename(
    AUTOGEN_SCHEMA_FILE, DOCS_FILE, config=GenerationConfiguration(minify=False)
)
print("Done..")
