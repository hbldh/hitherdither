#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
bayer_dithering
-----------

:copyright: 2016-09-09 by hbldh <henrik.blidh@nedomkull.com>

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import numpy as np


def B(n, transposed=False):
    """Get the Bayer matrix with side of length ``n``.

    Will only work if ``n`` is a power of 2.

    Reference: http://caca.zoy.org/study/part2.html

    :param int n: Power of 2 side length of matrix.
    :return: The Bayer matrix.

    """
    return (1 + I(n, transposed)) / (1 + (n * n))


def I(n, transposed=False):
    """Get the index matrix with side of length ``n``.

    Will only work if ``n`` is a power of 2.

    Reference: http://caca.zoy.org/study/part2.html

    :param int n: Power of 2 side length of matrix.
    :param bool transposed:
    :return: The index matrix.

    """
    if n == 2:
        if transposed:
            return np.array([[0, 3], [2, 1]], 'int')
        else:
            return np.array([[0, 2], [3, 1]], 'int')
    else:
        smaller_I = I(n >> 1, transposed)
        if transposed:
            return np.bmat([[4 * smaller_I, 4 * smaller_I + 3],
                            [4 * smaller_I + 2, 4 * smaller_I + 1]])
        else:
            return np.bmat([[4 * smaller_I,     4 * smaller_I + 2],
                            [4 * smaller_I + 3, 4 * smaller_I + 1]])


def bayer_dithering(image, palette, thresholds, order=8):
    """Render the image using the ordered Bayer matrix dithering pattern.

    :param :class:`PIL.Image` image: The image to apply
        Bayer ordered dithering to.
    :param :class:`~hitherdither.colour.Palette` palette: The palette to use.
    :param thresholds: Thresholds to apply dithering at.
    :param int order: The size of the Bayer matrix.
    :return:  The Bayer matrix dithered PIL image of type "P"
        using the input palette.

    """
    bayer_matrix = B(order)
    ni = np.array(image, 'uint8')
    thresholds = np.array(thresholds, 'uint8')
    xx, yy = np.meshgrid(range(ni.shape[1]), range(ni.shape[0]))
    xx %= order
    yy %= order
    factor_threshold_matrix = (np.expand_dims(
        bayer_matrix[yy, xx], axis=2) * thresholds)
    new_image = ni + factor_threshold_matrix
    return palette.create_PIL_png_from_rgb_array(new_image)
