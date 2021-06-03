#  Copyright 2021, Verizon Media
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

import json
from pkg_resources import resource_filename

from ychaos.testplan.schema import TestPlanSchema

print("Auto Generating Schema...")

PKG_RESOURCES = "ychaos.testplan.resources"
AUTOGEN_SCHEMA_FILE = str(resource_filename(PKG_RESOURCES, "schema.json"))
with open(AUTOGEN_SCHEMA_FILE, "w") as autogen_schema:
    json.dump(TestPlanSchema.schema(), autogen_schema, indent=4)
    autogen_schema.write("\n")

print("Done..")
