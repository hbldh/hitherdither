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

import pytest
try:
    import pathlib2 as pathlib
except ImportError:
    import pathlib

from hitherdither.data import _image


@pytest.fixture(scope='session')
def test_png():
    p = pathlib.Path(__file__).parent.joinpath('astronaut.png')
    url = 'https://raw.githubusercontent.com/scikit-image/scikit-image/master/skimage/data/astronaut.png'
    i = _image(p, url)
    return i


@pytest.fixture(scope='session')
def test_jpeg():
    p = pathlib.Path(__file__).parent.joinpath('rocket.jpg')
    url = 'https://raw.githubusercontent.com/scikit-image/scikit-image/master/skimage/data/rocket.jpg'
    i = _image(p, url)
    return i
