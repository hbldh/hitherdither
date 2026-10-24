#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tools
-----------

:copyright: 2017-05-10 by hbldh <henrik.blidh@nedomkull.com>

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import io

import numpy as np
import pytest
from PIL import Image
try:
    import pathlib2 as pathlib
except ImportError:
    import pathlib


def _synthetic_rgb():
    """Deterministic RGB test picture, so tests need no network access."""
    y, x = np.mgrid[0:96, 0:128]
    arr = np.stack(
        [(x * 2) % 256, (y * 2 + x) % 256, (255 - x * 2 + y) % 256], axis=2
    ).astype("uint8")
    return Image.fromarray(arr, "RGB")


@pytest.fixture(scope='session')
def test_png():
    return _synthetic_rgb()


@pytest.fixture(scope='session')
def test_jpeg():
    buf = io.BytesIO()
    _synthetic_rgb().save(buf, "JPEG", quality=75)
    buf.seek(0)
    img = Image.open(buf)
    img.load()
    return img
