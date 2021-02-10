#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

import xml.etree.ElementTree as Etree
import os
import json
from pprint import pprint

COVERAGE_THRESHOLD = 70
SONAR_URL = "https://sonar.screwdriver.ouroath.com/dashboard?id=pipeline:{pipeline_id}&pullRequest={pr_num}"

PR_NUM = os.getenv("SD_PULL_REQUEST", 1)
PIPELINE_ID = os.getenv("SD_PIPELINE_ID", "1041241")

COVERAGE_FILE = f"{os.getenv('SD_ARTIFACTS_DIR')}/coverage/cobertura.xml"

with open(COVERAGE_FILE, "r") as coverage_file:
    tree = Etree.parse(coverage_file)

root = tree.getroot()
root_attributes = root.attrib

coverage_percent = (
    int(root_attributes["lines-covered"]) / int(root_attributes["lines-valid"]) * 100
)

if coverage_percent < COVERAGE_THRESHOLD:
    meta_status = {
        "status": "FAILURE",
        "message": f"Coverage = {coverage_percent}% (Expected = {COVERAGE_THRESHOLD}%)",
        "url": SONAR_URL.format(pr_num=PR_NUM, pipeline_id=PIPELINE_ID),
    }
else:
    meta_status = {
        "status": "SUCCESS",
        "message": f"Coverage = {coverage_percent}%",
        "url": SONAR_URL.format(pr_num=PR_NUM, pipeline_id=PIPELINE_ID),
    }

pprint(meta_status)

# Sets Coverage as a check in PR build
# https://git.vzbuilders.com/pages/cocktails-screwdriver/v4-guide/user-guide/metadata.html#coverage-and-test-results
os.system(
    f"meta set meta.status.coverage '{json.dumps(meta_status, separators=(',', ':'))}'"
)
