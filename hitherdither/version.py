#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
version.py
-----------

:copyright: 2017-05-10 by hbldh <henrik.blidh@nedomkull.com>

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re

# Version information.
__version__ = '0.1.4.dev2'
version = __version__  # backwards compatibility name
try:
    version_info = [int(x) if x.isdigit() else x for x in
                    re.match('^([0-9]+)\.([0-9]+)[\.]*([0-9]*)(.*)$',
                             __version__, re.DOTALL).groups()]
except Exception:
    version_info = ()
