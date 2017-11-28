#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`diffusion`
=======================

.. moduleauthor:: hbldh <henrik.blidh@swedwise.com>
Created on 2016-09-12, 11:34

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import numpy as np

_DIFFUSION_MAPS = {
    'floyd-steinberg': (
        (1, 0,  7 / 16),
        (-1, 1, 3 / 16),
        (0, 1,  5 / 16),
        (1, 1,  1 / 16)
    ),
    'atkinson': (
        (1, 0,  1 / 8),
        (2, 0,  1 / 8),
        (-1, 1, 1 / 8),
        (0, 1,  1 / 8),
        (1, 1,  1 / 8),
        (0, 2,  1 / 8),
    ),
    'jarvis-judice-ninke': (
        (1, 0,  7 / 48),
        (2, 0,  5 / 48),
        (-2, 1, 3 / 48),
        (-1, 1, 5 / 48),
        (0, 1,  7 / 48),
        (1, 1,  5 / 48),
        (2, 1,  3 / 48),
        (-2, 2, 1 / 48),
        (-1, 2, 3 / 48),
        (0, 2,  5 / 48),
        (1, 2,  3 / 48),
        (2, 2,  1 / 48),
    ),
    'stucki': (
        (1, 0,  8 / 42),
        (2, 0,  4 / 42),
        (-2, 1, 2 / 42),
        (-1, 1, 4 / 42),
        (0, 1,  8 / 42),
        (1, 1,  4 / 42),
        (2, 1,  2 / 42),
        (-2, 2, 1 / 42),
        (-1, 2, 2 / 42),
        (0, 2,  4 / 42),
        (1, 2,  2 / 42),
        (2, 2,  1 / 42),
    ),
    'burkes': (
        (1, 0,  8 / 32),
        (2, 0,  4 / 32),
        (-2, 1, 2 / 32),
        (-1, 1, 4 / 32),
        (0, 1,  8 / 32),
        (1, 1,  4 / 32),
        (2, 1,  2 / 32),
    ),
    'sierra3': (
        (1, 0,  5 / 32),
        (2, 0,  3 / 32),
        (-2, 1, 2 / 32),
        (-1, 1, 4 / 32),
        (0, 1,  5 / 32),
        (1, 1,  4 / 32),
        (2, 1,  2 / 32),
        (-1, 2, 2 / 32),
        (0, 2,  3 / 32),
        (1, 2,  2 / 32),
    ),
    'sierra2': (
        (1, 0,  4 / 16),
        (2, 0,  3 / 16),
        (-2, 1, 1 / 16),
        (-1, 1, 2 / 16),
        (0, 1,  3 / 16),
        (1, 1,  2 / 16),
        (2, 1,  1 / 16),
    ),
    'sierra-2-4a': (
        (1, 0,  2 / 4),
        (-1, 1, 1 / 4),
        (0, 1,  1 / 4),
    ),
    'stevenson-arce': (
        (2, 0,   32 / 200),
        (-3, 1,  12 / 200),
        (-1, 1,  26 / 200),
        (1, 1,   30 / 200),
        (3, 1,   30 / 200),
        (-2, 2,  12 / 200),
        (0, 2,   26 / 200),
        (2, 2,   12 / 200),
        (-3, 3,   5 / 200),
        (-1, 3,  12 / 200),
        (1, 3,   12 / 200),
        (3, 3,    5 / 200)
    )
}


def error_diffusion_dithering(image, palette, method='floyd-steinberg',
                              order=2):
    """Perform image dithering by error diffusion method.

    .. note:: Error diffusion is totally unoptimized and therefore very slow.
        It is included more as a reference implementation than as a useful
        method.

    Reference:
        http://bisqwit.iki.fi/jutut/kuvat/ordered_dither/error_diffusion.txt

    Quantization error of *current* pixel is added to the pixels
    on the right and below according to the formulas below.
    This works nicely for most static pictures, but causes
    an avalanche of jittering artifacts if used in animation.

    Floyd-Steinberg:

              *  7
           3  5  1      / 16

    Jarvis-Judice-Ninke:

              *  7  5
        3  5  7  5  3
        1  3  5  3  1   / 48

    Stucki:

              *  8  4
        2  4  8  4  2
        1  2  4  2  1   / 42

    Burkes:

              *  8  4
        2  4  8  4  2   / 32


    Sierra3:

              *  5  3
        2  4  5  4  2
           2  3  2      / 32

    Sierra2:

              *  4  3
        1  2  3  2  1   / 16

    Sierra-2-4A:

              *  2
           1  1         / 4

    Stevenson-Arce:

                      *   .  32
        12   .   26   .  30   .  16
        .   12    .  26   .  12   .
        5    .   12   .  12   .   5    / 200

    Atkinson:

              *   1   1    / 8
          1   1   1
              1

    :param :class:`PIL.Image` image: The image to apply error
        diffusion dithering to.
    :param :class:`~hitherdither.colour.Palette` palette: The palette to use.
    :param str method: The error diffusion map to use.
    :param int order: Metric parameter ``ord`` to send to
        :method:`numpy.linalg.norm`.
    :return: The error diffusion dithered PIL image of type
        "P" using the input palette.

    """
    ni = np.array(image, 'float')

    diff_map = _DIFFUSION_MAPS.get(method.lower())

    for y in range(ni.shape[0]):
        for x in range(ni.shape[1]):
            old_pixel = ni[y, x]
            old_pixel[old_pixel < 0.0] = 0.0
            old_pixel[old_pixel > 255.0] = 255.0
            new_pixel = palette.pixel_closest_colour(old_pixel, order)
            quantization_error = old_pixel - new_pixel
            ni[y, x] = new_pixel
            for dx, dy, diffusion_coefficient in diff_map:
                xn, yn = x + dx, y + dy
                if (0 <= xn < ni.shape[1]) and (0 <= yn < ni.shape[0]):
                    ni[yn, xn] += quantization_error * diffusion_coefficient
    return palette.create_PIL_png_from_rgb_array(np.array(ni, 'uint8'))
