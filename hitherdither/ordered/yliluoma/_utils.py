#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
_utils
-----------

:copyright: 2016-09-23 by hbldh <henrik.blidh@nedomkull.com>

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import numpy as np

# CCIR 601 luminosity
CCIR_LUMINOSITY = np.array([299.0, 587.0, 114.0])


def color_compare(c1, c2):
    """Compare the difference of two RGB values, weigh by CCIR 601 luminosity

    double ColorCompare(int r1,int g1,int b1, int r2,int g2,int b2)
    {
        double luma1 = (r1*299 + g1*587 + b1*114) / (255.0*1000);
        double luma2 = (r2*299 + g2*587 + b2*114) / (255.0*1000);
        double lumadiff = luma1-luma2;
        double diffR = (r1-r2)/255.0, diffG = (g1-g2)/255.0, diffB = (b1-b2)/255.0;
        return (diffR*diffR*0.299 + diffG*diffG*0.587 + diffB*diffB*0.114)*0.75
             + lumadiff*lumadiff;
    }

    :return: float

    """
    luma_diff = (c1.dot(CCIR_LUMINOSITY) / (255.0 * 1000.0) -
                 c2.dot(CCIR_LUMINOSITY) / (255.0 * 1000.0))
    diff_col = (c1 - c2) / 255.0
    return (((diff_col ** 2).dot(CCIR_LUMINOSITY / 1000.0) * 0.75) +
            (luma_diff ** 2))
