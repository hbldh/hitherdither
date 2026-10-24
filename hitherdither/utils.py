#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Image conversion helpers.

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import


import numpy as np
from PIL import Image


def np2pil(img):
    return Image.fromarray(np.array(img, "uint8"))


def pil2np(img):
    return np.array(img, "uint8")


def to_rgb_array(image, dtype="float"):
    """Get an ``[M x N x 3]`` RGB array from (almost) any image.

    PIL images of mode other than ``RGB`` (``L``, ``1``, ``LA``, ``RGBA``,
    ``P``, ``CMYK``, ...) are converted with ``image.convert("RGB")``.
    Numpy arrays are accepted as well: 2-D arrays (and ``[M x N x 1]``) are
    treated as greyscale, ``[M x N x 4]`` arrays as RGBA (alpha dropped).

    :param image: A PIL image or a numpy array.
    :param dtype: Data type of the returned array.
    :return: A new array of shape ``[M x N x 3]``.

    """
    if isinstance(image, Image.Image):
        if image.mode != "RGB":
            image = image.convert("RGB")
        return np.array(image, dtype)
    arr = np.array(image, dtype)
    if arr.ndim == 2:
        arr = np.repeat(arr[:, :, np.newaxis], 3, axis=2)
    elif arr.ndim == 3 and arr.shape[2] == 1:
        arr = np.repeat(arr, 3, axis=2)
    elif arr.ndim == 3 and arr.shape[2] == 4:
        arr = arr[:, :, :3].copy()
    if arr.ndim != 3 or arr.shape[2] != 3:
        raise ValueError(
            "Cannot interpret array of shape {0} as an image.".format(arr.shape)
        )
    return arr
