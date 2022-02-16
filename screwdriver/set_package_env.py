#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

import distutils.errors
import logging
import os
from pkg_resources import safe_name
from setuptools.config import read_configuration


def package_dir(conf_dict):
    pdir = "."
    for dirname in ["src"]:
        if os.path.exists(dirname):
            pdir = dirname
            break
    try:
        conf_dict = read_configuration("setup.cfg")
    except distutils.errors.DistutilsFileError:
        return pdir
    conf_options = conf_dict.get("options", {})
    conf_metadata = conf_dict.get("metadata", {})
    if conf_options and conf_options.get("package_dir", {}):
        pdir = list(conf_options["package_dir"].values())[0]
    elif (
        pdir == "."
        and "name" in conf_metadata.keys()
        and os.path.exists(conf_metadata["name"])
    ):
        return conf_metadata["name"]
    return pdir


conf_dict = {
    "metadata": {
        "name": "unknown",
        "version": "unknown",
    }
}
try:
    conf_dict.update(read_configuration("setup.cfg"))
except distutils.errors.DistutilsFileError:
    logging.debug(
        "The setup.cfg configuration file not found, cannot determine package name and version"
    )
artifact_dir = os.environ.get("SD_ARTIFACTS_DIR", "artifacts")
env_dir = f"{artifact_dir}/env"
env_filename = f"{env_dir}/package.env"
os.makedirs(env_dir, exist_ok=True)
with open(env_filename, "w") as env_handle:
    env_handle.write(f'PACKAGE_NAME="{safe_name(conf_dict["metadata"]["name"])}"\n')
    env_handle.write(f'PACKAGE_VERSION="{conf_dict["metadata"]["version"]}"\n')
    env_handle.write(f'PACKAGE_DIR="{package_dir(conf_dict)}"\n')
    env_handle.write("export PACKAGE_NAME\n")
    env_handle.write("export PACKAGE_VERSION\n")
    env_handle.write("export PACKAGE_DIR\n")
