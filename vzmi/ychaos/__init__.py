#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

"""
vzmi.ychaos module
"""

from typing import List

import pkg_resources

__all__: List[str] = ["__version__"]
__copyright__: str = "Copyright 2021, Verizon Media Inc."
__version__: str = pkg_resources.get_distribution("vzmi.ychaos").version
