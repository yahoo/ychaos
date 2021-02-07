import os
import subprocess


def get_package_version():
    try:
        cmd = "meta get package.version"
        return "v" + str(subprocess.check_output(cmd.split()), encoding="UTF-8")
    except Exception as e:
        try:
            cmd = "git ls-remote --tags --sort=v:refname git@git.vzbuilders.com:ssharma06/vzmi.ychaos"
            return (
                str(subprocess.check_output(cmd.split()), encoding="UTF-8")
                .strip()
                .splitlines()[-1]
                .strip("^{}")
                .split("/")[-1]
            )
        except Exception as e2:
            return "Unknown"


version = get_package_version()
os.system(f"meta set label '{version}'")
