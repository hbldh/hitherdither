#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
algorithm_one
-----------

:copyright: 2016-09-12 by hbldh <henrik.blidh@nedomkull.com>

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import numpy as np
from ..bayer import B


def yliluomas_1_ordered_dithering(image, palette, order=8):
    bayer_matrix = B(order)
    ni = np.array(image, 'uint8')
    xx, yy = np.meshgrid(range(ni.shape[1]), range(ni.shape[0]))
    factor_matrix = bayer_matrix[yy % order, xx % order]

    color_matrix = np.zeros(factor_matrix.shape, dtype='int')
    for x, y in zip(np.nditer(xx), np.nditer(yy)):
        plan = _devise_best_mixing_plan(palette, ni[y, x, :], order=order)
        color_matrix[y, x] = plan[0] if plan[-1] < factor_matrix[y, x] else plan[1]
    return palette.render(color_matrix)


def _color_compare(rgb1, rgb2):
    """Compare two colours.

    .. code:: cpp

        // Compare the difference of two RGB values
        double ColorCompare(int r1,int g1,int b1, int r2,int g2,int b2)
        {
            double diffR = (r1-r2)/255.0, diffG = (g1-g2)/255.0, diffB = (b1-b2)/255.0;
            return diffR*diffR + diffG*diffG + diffB*diffB;
        }

    :return:
    """
    return (((np.array(rgb1) - np.array(rgb2)) / 255.0) ** 2).sum()


def _evaluate_mixing_error(rgb_desired, rgb_mix, rgb1, rgb2, ratio):
    """Evaluate the mixing error.

    .. code:: cpp

        double EvaluateMixingError(int r,int g,int b,    // Desired color
                           int r0,int g0,int b0, // Mathematical mix product
                           int r1,int g1,int b1, // Mix component 1
                           int r2,int g2,int b2, // Mix component 2
                           double ratio)         // Mixing ratio
        {
            return ColorCompare(r,g,b, r0,g0,b0);
        }

    :param rgb_desired:
    :param rgb_mix:
    :param rgb1:
    :param rgb2:
    :param ratio:
    :return:

    """
    return _color_compare(rgb_desired, rgb_mix)


def _devise_best_mixing_plan(palette, colour, order=8):
    """Find the best mixing plan

    Pre-calculate this eventually.

    :param palette:
    :param colour:
    :param order:
    :return:

    """
    r, g, b = colour
    least_penalty = 1e99

    nn = float(order * order)
    results = ()

    for i in range(len(palette)):
        for j in range(i + 1, len(palette)):
            for ratio in range(order * order):
                if i == j and ratio != 0:
                    break
                    # Determine the two component colors.
                c1, c2 = palette[i], palette[j]
                c_mix = c1 + np.array(ratio * (c2 - c1), 'uint8') / nn
                penalty = _evaluate_mixing_error(
                    colour, c_mix, c1, c2, ratio / nn)
                if penalty < least_penalty:
                    least_penalty = penalty
                    results = (i, j, ratio / 64.)
    return results
