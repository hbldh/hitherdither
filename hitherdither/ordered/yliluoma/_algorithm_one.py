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

# CCIR 601 luminosity
CCIR_LUMINOSITY = np.array([299.0, 587.0, 114.0])

def _get_mixing_plan_matrix(palette, order=8, improved_metric=True):
    mixing_matrix = []
    colours = {}
    colour_component_distances = []

    nn = order * order
    for i in range(len(palette)):
        for j in range(i + 1, len(palette)):
            for ratio in range(nn):
                # Determine the two component colors.
                c_mix = _colour_combine(palette, i, j, ratio / nn)
                hex_colour = palette.rgb2hex(*c_mix.tolist())
                colours[hex_colour] = (i, j, ratio / nn)
                mixing_matrix.append(c_mix)

                c1 = np.array(palette[i], 'int')
                c2 = np.array(palette[j], 'int')
                if improved_metric:
                    luma1 = c1.dot(CCIR_LUMINOSITY) / (255.0 * 1000.0)
                    luma2 = c2.dot(CCIR_LUMINOSITY) / (255.0 * 1000.0)
                    luma_diff = luma1 - luma2
                    cmpval = (((c1 - c2) * (c1 - c2) * CCIR_LUMINOSITY) /
                              (255.0 * 1000.0)).sum() * 0.75 + (luma_diff * luma_diff)
                    colour_component_distances.append(cmpval)
                else:
                    colour_component_distances.append(np.linalg.norm(c1 - c2))

    mixing_matrix = np.array(mixing_matrix)
    colour_component_distances = np.array(colour_component_distances)

    for c in mixing_matrix:
        assert palette.rgb2hex(*c.tolist()) in colours

    return mixing_matrix, colours, colour_component_distances


def _colour_combine(palette, i, j, ratio):
    c1, c2 = np.array(palette[i], 'int'), np.array(palette[j], 'int')
    return np.array(c1 + ratio * (c2 - c1), 'uint8')


def _standard_mixing_error_fcn(
        colour, mixing_matrix, colour_component_distances):
    return (np.linalg.norm(
        np.array(colour, 'int') - mixing_matrix, axis=1, ord=2) +
            colour_component_distances * 0.1)


def _improved_mixing_error_fcn(
        colour, mixing_matrix,
        colour_component_distances, luma_mat=None):
    """Compares two colours using the Psychovisual model.

    The simplest way to adjust the psychovisual model is to
    add some code that considers the difference between the
    two pixel values that are being mixed in the dithering
    process, and penalizes combinations that differ too much.

    Wikipedia has an entire article about the topic of comparing
    two color values. Most of the improved color comparison
    functions are based on the CIE colorspace, but simple
    improvements can be done in the RGB space too. Such a simple
    improvement is shown below. We might call this RGBL, for
    luminance-weighted RGB.

    :param :class:`numpy.ndarray` colour:The colour
    :param :class:`numpy.ndarray` mixing_matrix:
    :param :class:`numpy.ndarray` colour_component_distances:
    :return: :class:`numpy.ndarray`

    """
    colour = np.array(colour, 'int')
    if luma_mat is not None:
        luma_mat = (mixing_matrix * CCIR_LUMINOSITY).sum(axis=1) / (255.0 * 1000.0)
    luma_colour = colour.dot(CCIR_LUMINOSITY) / (255.0 * 1000.0)
    luma_diff = luma_mat - luma_colour
    diff_colour = colour - mixing_matrix
    cmpvals = (diff_colour * diff_colour).dot(CCIR_LUMINOSITY) / (255.0 * 1000.0)
    cmpvals *= 0.75
    cmpvals += luma_diff * luma_diff
    cmpvals += colour_component_distances * 0.1
    return cmpvals


def yliluomas_1_ordered_dithering(image, palette, order=8, improved_metric=True):
    bayer_matrix = B(order)
    ni = np.array(image, 'uint8')
    xx, yy = np.meshgrid(range(ni.shape[1]), range(ni.shape[0]))
    factor_matrix = bayer_matrix[yy % order, xx % order]

    mixing_matrix, colour_map, colour_component_distances = \
        _get_mixing_plan_matrix(palette, improved_metric=improved_metric)
    mixing_matrix = np.array(mixing_matrix, 'int')
    if improved_metric:
        luma_mat = ((mixing_matrix * CCIR_LUMINOSITY).sum(axis=1) /
                    (255.0 * 1000.0))

    color_matrix = np.zeros(factor_matrix.shape, dtype='uint8')
    for x, y in zip(np.nditer(xx), np.nditer(yy)):
        if improved_metric:
            min_index = np.argmin(_improved_mixing_error_fcn(
                ni[y, x, :], mixing_matrix,
                colour_component_distances, luma_mat))
        else:
            min_index = np.argmin(_standard_mixing_error_fcn(
                ni[y, x, :], mixing_matrix, colour_component_distances))
        closest_mix_colour = mixing_matrix[min_index, :].tolist()
        closest_mix_hexcolour = palette.rgb2hex(*closest_mix_colour)
        plan = colour_map.get(closest_mix_hexcolour)
        color_matrix[y, x] = (plan[0] if (plan[-1] < factor_matrix[y, x])
                              else plan[1])

    return palette.create_PIL_png_from_closest_colour(color_matrix)
