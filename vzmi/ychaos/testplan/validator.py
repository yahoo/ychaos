from pathlib import Path
from typing import Union

import yaml

from vzmi.ychaos.testplan.schema import TestPlan


class TestPlanValidator:
    @classmethod
    def validate_file(cls, path: Union[str, Path]):
        path = Path(path)
        with open(path, "r") as file:
            data = yaml.safe_load(file)

        cls.validate_data(data)

    @classmethod
    def validate_data(cls, data):
        TestPlan.validate(data)
