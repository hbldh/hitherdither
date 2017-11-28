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

_CLUSTER_DOT_MATRICES = {
    4: np.array([[12, 5, 6, 13],
                 [4, 0, 1, 7],
                 [11, 3, 2, 8],
                 [15, 10, 9, 14]], 'float') / 16.0,
    8: np.array([[24, 10, 12, 26, 35, 47, 49, 37],
                 [8, 0, 2, 14, 45, 59, 61, 51],
                 [22, 6, 4, 16, 43, 57, 63, 53],
                 [30, 20, 18, 28, 33, 41, 55, 39],
                 [34, 46, 48, 36, 25, 11, 13, 27],
                 [44, 57, 60, 50, 9, 1, 3, 15],
                 [42, 56, 62, 52, 23, 7, 5, 17],
                 [32, 40, 54, 38, 31, 21, 19, 29]], 'float') / 64.0,
    (5, 3): np.array([[9, 3, 0, 6, 12],
                      [10, 4, 1, 7, 13],
                      [11, 5, 2, 8, 14]], 'float') / 15.0,
}


def cluster_dot_dithering(image, palette, thresholds, order=4):
    """Render the image using the ordered Bayer matrix dithering pattern.

    Reference: http://caca.zoy.org/study/part2.html

    :param :class:`PIL.Image` image: The image to apply the
        ordered dithering to.
    :param :class:`~hitherdither.colour.Palette` palette: The palette to use.
    :param thresholds: Thresholds to apply dithering at.
    :param int order: The size of the Bayer matrix.
    :return:  The Bayer matrix dithered PIL image of type "P"
        using the input palette.

    """

    cluster_dot_matrix = _CLUSTER_DOT_MATRICES.get(order)
    if cluster_dot_matrix is None:
        raise NotImplementedError(
            "Only order 4 and 8 is implemented as of yet.")
    ni = np.array(image, 'uint8')
    thresholds = np.array(thresholds, 'uint8')
    xx, yy = np.meshgrid(range(ni.shape[1]), range(ni.shape[0]))
    xx %= order
    yy %= order
    factor_threshold_matrix = (
        np.expand_dims(cluster_dot_matrix[yy, xx], axis=2) * thresholds)
    new_image = ni + factor_threshold_matrix
    return palette.create_PIL_png_from_rgb_array(new_image)
