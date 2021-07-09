#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import shlex
import subprocess  # nosec: using shlex

from pydantic import validate_arguments

from ....testplan.verification import PythonModuleVerification
from ..data import VerificationData, VerificationStateData
from .BaseVerificationPlugin import BaseVerificationPlugin


class PythonModuleVerificationPlugin(BaseVerificationPlugin):

    __verification_type__ = "python_module"

    @validate_arguments
    def __init__(self, config: PythonModuleVerification, state_data: VerificationData):
        super(PythonModuleVerificationPlugin, self).__init__(config, state_data)

    def run_verification(self) -> VerificationStateData:
        _command = [self.config.executable, shlex.quote(str(self.config.path))]
        _command.extend(self.config.safe_arguments())
        completed_process: subprocess.CompletedProcess = (
            subprocess.run(  # nosec: Using shlex
                _command, stderr=subprocess.PIPE, timeout=10
            )
        )
        return VerificationStateData(
            rc=completed_process.returncode,
            type=self.__verification_type__,
            data=dict(stdout=completed_process.stdout, stderr=completed_process.stderr),
        )
