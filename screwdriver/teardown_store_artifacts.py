#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

import glob
import os
import shutil


CONFIGFILES = [
    ".bandit.ini",
    "bandit.ini",
    ".coveragerc",
    "coveragerc",
    "MANIFEST.in",
    "pyproject.toml",
    "requirements.txt",
    "setup.cfg",
    "setup.py",
    ".pylintrc",
    "pylintrc",
    "tox.ini",
] + glob.glob("*.ini")

if "PYLINTRC" in os.environ.keys():
    CONFIGFILES.append(os.environ["PYLINTRC"])
LOGFILES = (
    glob.glob("*.log") + glob.glob(".tox/log/*.log") + glob.glob(".tox/*/log/*.log")
)
artifacts_dir = os.environ.get("SD_ARTIFACTS_DIR", ".")
config_dir = os.path.join(artifacts_dir, "config")
log_dir = os.path.join(artifacts_dir, "logs")
report_dir = os.path.join(artifacts_dir, "reports")
os.makedirs(config_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)
os.makedirs(report_dir, exist_ok=True)
if os.path.exists("artifacts") and artifacts_dir != ".":
    print(f"Copying artifacts -> {artifacts_dir}", flush=True)
    try:
        shutil.copytree("artifacts", artifacts_dir, dirs_exist_ok=True)
    except TypeError:
        try:
            shutil.copytree("artifacts", artifacts_dir)
        except FileExistsError:
            pass
for configfile in CONFIGFILES:
    if os.path.exists(configfile):
        print(f"Copying config file {configfile} -> {config_dir}", flush=True)
        shutil.copy(configfile, os.path.join(config_dir, configfile))
for logfile in LOGFILES:
    dirpath = os.path.dirname(logfile)
    destdir = log_dir
    if dirpath:
        destdir = os.path.join(log_dir, dirpath)
        os.makedirs(destdir, exist_ok=True)
    if os.path.exists(logfile):
        print(f"Copying log file {logfile} -> {destdir}", flush=True)
        shutil.copy(logfile, destdir)
