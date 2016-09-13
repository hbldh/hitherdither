#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`test_palette`
=======================

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>
Created on 2016-09-13, 09:38

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import pytest
import numpy as np

from hitherdither import palette

@pytest.mark.parametrize("hex_colour, rgb_colour", (("#ffffff", (255,255,255)),
                                                    ("#abcdef", (171,205,239)),
                                                    ("#012345", (1, 35, 69)),
                                                    (0x82f698, (130, 246, 152)),
                                                    ("0x82f698", (130, 246, 152))))
def test_hex2rgb(hex_colour, rgb_colour):
    assert palette.hex2rgb(hex_colour) == rgb_colour


@pytest.mark.parametrize("hex_colour, rgb_colour", (("#ffffff", (255,255,255)),
                                                    ("#abcdef", (171,205,239)),
                                                    ("#012345", (1, 35, 69)),
                                                    (0x82f698, (130, 246, 152)),
                                                    ("0x82f698", (130, 246, 152))))
def test_rgb2hex(hex_colour, rgb_colour):
    try:
        if isinstance(hex_colour, int):
            hc = hex_colour
        else:
            hc = int(hex_colour, 16)
    except:
        hc = int(hex_colour[1:], 16)
    assert palette.rgb2hex(*rgb_colour) == hc