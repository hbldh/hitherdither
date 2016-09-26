#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import re

from . import data
from . import math
from . import ordered
from . import diffusion
from . import palette
from . import utils


# Version information.
__version__ = '0.1.3'
version = __version__  # backwards compatibility name
try:
    version_info = [int(x) if x.isdigit() else x for x in
                    re.match('^([0-9]+)\.([0-9]+)[\.]*([0-9]*)(.*)$',
                             __version__, re.DOTALL).groups()]
except Exception:
    version_info = ()
