#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`run`
=======================

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>
Created on 2016-09-12, 09:44

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import numpy as np

from hitherdither import data
from hitherdither.palette import Palette
from hitherdither.diffusion import error_diffusion_dithering
from hitherdither.ordered import yliluoma
import hitherdither.utils

# Fetch the example image and the palette from Yliluoma's page.
s = data.scene()
p = Palette(hitherdither.data.palette())

p2 = Palette.create_by_median_cut(s)

# Map raw image to the palette
closest_colour = p.image_closest_colour(s, order=2)
# Render the undithered image with only colours in
# the palette as a RGB numpy array.
undithered_image = p.render(closest_colour)
# Create a PIL Image of mode "P" from the palette colour index matrix.
s_png = p.create_PIL_png_from_closest_colour(closest_colour)
s_png.show()

#print(np.linalg.norm(undithered_image - np.array(s_png.convert("RGB"))))

# Render an Yliluoma algorithm 1 image.
yliluoma1_image = yliluoma.yliluomas_1_ordered_dithering(
    s, p, order=8)
yliluoma1_image.resize(np.array(yliluoma1_image.size) * 4).show()
#yliluoma1_image.show()

