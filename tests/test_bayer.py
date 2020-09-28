#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`test_bayer`
=======================

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>
Created on 2016-09-12, 13:35

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import pytest
import numpy as np

from hitherdither.ordered import bayer


_BAYER_MATRICES = {
    2: (1 / 5.) * np.array([
        [1, 3],
        [4, 2]]
    ),
    3: (1 / 10.) * np.array([
        [1, 8, 4],
        [7, 6, 3],
        [5, 2, 9]]
    ),
    4: (1 / 17.) * np.array(
        [[1, 9, 3, 11],
         [13, 5, 15, 7],
         [4, 12, 2, 10],
         [16, 8, 14, 6]]
    ),
    8: 1 / 65. * np.array([
        [1, 49, 13, 61, 4, 52, 16, 64],
        [33, 17, 45, 29, 36, 20, 48, 32],
        [9, 57, 5, 53, 12, 60, 8, 56],
        [41, 25, 37, 21, 44, 28, 40, 24],
        [3, 51, 15, 63, 2, 50, 14, 62],
        [35, 19, 47, 31, 34, 18, 46, 30],
        [11, 59, 7, 55, 10, 58, 6, 54],
        [43, 27, 39, 23, 42, 26, 38, 22]]
    ).T
}

@pytest.mark.parametrize("order", [2,4,8])
def test_bayer(order):
    np.testing.assert_allclose(bayer.B(order, False), _BAYER_MATRICES.get(order))


