#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
algorithm_one
-----------

:copyright: 2016-09-12 by hbldh <henrik.blidh@nedomkull.com>

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from ._utils import color_compare, CCIR_LUMINOSITY
from ..bayer import I


def _get_mixing_plan_matrix(palette, order=8):
    mixing_matrix = []
    colours = {}
    colour_component_distances = []

    nn = order * order
    for i in range(len(palette)):
        for j in range(i, len(palette)):
            for ratio in range(0, nn):
                if i == j and ratio != 0:
                    break
                # Determine the two component colors.
                c_mix = _colour_combine(palette, i, j, ratio / nn)
                hex_colour = palette.rgb2hex(*c_mix.tolist())
                colours[hex_colour] = (i, j, ratio / nn)
                mixing_matrix.append(c_mix)

                c1 = np.array(palette[i], 'int')
                c2 = np.array(palette[j], 'int')
                cmpval = color_compare(c1, c2) * 0.1 * \
                    (np.abs((ratio / float(nn)) - 0.5) + 0.5)
                colour_component_distances.append(cmpval)

    mixing_matrix = np.array(mixing_matrix)
    colour_component_distances = np.array(colour_component_distances)

    for c in mixing_matrix:
        assert palette.rgb2hex(*c.tolist()) in colours

    return mixing_matrix, colours, colour_component_distances


def _colour_combine(palette, i, j, ratio):
    c1, c2 = np.array(palette[i], 'int'), np.array(palette[j], 'int')
    return np.array(c1 + ratio * (c2 - c1), 'uint8')


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

    :param :class:`numpy.ndarray` colour: The colour to estimate error to.
    :param :class:`numpy.ndarray` mixing_matrix: The rgb
        values of mixed colours.
    :param :class:`numpy.ndarray` colour_component_distances: The colour
        distance of the mixed colours.
    :return: :class:`numpy.ndarray`

    """
    colour = np.array(colour, 'int')
    if luma_mat is None:
        luma_mat = mixing_matrix.dot(CCIR_LUMINOSITY / 1000.0 / 255.0)
    luma_colour = colour.dot(CCIR_LUMINOSITY) / (255.0 * 1000.0)
    luma_diff_squared = (luma_mat - luma_colour) ** 2
    diff_colour_squared = ((colour - mixing_matrix) / 255.0) ** 2
    cmpvals = diff_colour_squared.dot(CCIR_LUMINOSITY) / 1000.0
    cmpvals *= 0.75
    cmpvals += luma_diff_squared
    cmpvals += colour_component_distances
    return cmpvals


def yliluomas_1_ordered_dithering(image, palette, order=8):
    """A dithering method that weighs in color combinations of palette.

    N.B. tri-tone dithering is not implemented.

    :param :class:`PIL.Image` image: The image to apply
        Bayer ordered dithering to.
    :param :class:`~hitherdither.colour.Palette` palette: The palette to use.
    :param int order: The Bayer matrix size to use.
    :return:  The dithered PIL image of type "P" using the input palette.

    """
    bayer_matrix = I(order, transposed=True) / 64.0
    ni = np.array(image, 'uint8')
    xx, yy = np.meshgrid(range(ni.shape[1]), range(ni.shape[0]))
    factor_matrix = bayer_matrix[yy % order, xx % order]

    # Prepare all precalculated mixed colours and their respective
    mixing_matrix, colour_map, colour_component_distances = \
        _get_mixing_plan_matrix(palette)
    mixing_matrix = np.array(mixing_matrix, 'int')
    luma_mat = mixing_matrix.dot(CCIR_LUMINOSITY / 1000.0 / 255.0)

    color_matrix = np.zeros(ni.shape[:2], dtype='uint8')
    for x, y in zip(np.nditer(xx), np.nditer(yy)):

        min_index = np.argmin(_improved_mixing_error_fcn(
            ni[y, x, :], mixing_matrix,
            colour_component_distances, luma_mat))
        closest_mix_colour = mixing_matrix[min_index, :].tolist()
        closest_mix_hexcolour = palette.rgb2hex(*closest_mix_colour)
        plan = colour_map.get(closest_mix_hexcolour)
        color_matrix[y, x] = (plan[1] if (factor_matrix[y, x] < plan[-1])
                              else plan[0])

    return palette.create_PIL_png_from_closest_colour(color_matrix)


def _evaluate_mixing_error(desired_colour, mixed_colour,
                           component_colour_1, component_colour_2,
                           ratio, component_colour_compare_value=None):
    """Compare colours and weigh in component difference.

    double EvaluateMixingError(int r,int g,int b,
                               int r0,int g0,int b0,
                               int r1,int g1,int b1,
                               int r2,int g2,int b2,
                               double ratio)
    {
        return ColorCompare(r,g,b, r0,g0,b0)
             + ColorCompare(r1,g1,b1, r2,g2,b2) * 0.1
             * (fabs(ratio-0.5)+0.5);
    }


    :param desired_colour:
    :param mixed_colour:
    :param component_colour_1:
    :param component_colour_2:
    :param ratio:
    :param component_colour_compare_value:
    :return:

    """
    if component_colour_compare_value is None:
        return (color_compare(desired_colour, mixed_colour) +
                (color_compare(component_colour_1, component_colour_2) *
                 0.1 * (np.abs(ratio - 0.5) + 0.5)))
    else:
        return (color_compare(desired_colour, mixed_colour) +
                component_colour_compare_value)
