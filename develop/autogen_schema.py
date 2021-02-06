import json
from pkg_resources import resource_filename

from vzmi.ychaos.testplan.schema import TestPlanSchema

print("Auto Generating Schema...")

PKG_RESOURCES = "vzmi.ychaos.testplan.resources"
AUTOGEN_SCHEMA_FILE = str(resource_filename(PKG_RESOURCES, "schema.json"))

with open(AUTOGEN_SCHEMA_FILE, "w") as autoGenSchema:
    json.dump(TestPlanSchema.schema(), autoGenSchema, indent=4)
    autoGenSchema.write("\n")
