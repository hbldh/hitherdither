#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
palette
-----------

:copyright: 2016-09-09 by hbldh <henrik.blidh@nedomkull.com>

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import numpy as np
from PIL import Image
from PIL.ImagePalette import ImagePalette

from hitherdither.exceptions import PaletteCouldNotBeCreatedError

try:
    string_type = basestring
except NameError:
    string_type = str


def hex2rgb(h):
    if isinstance(h, string_type):
        return hex2rgb(int(h[1:] if h.startswith('#') else h, 16))
    return (h >> 16) & 0xff, (h >> 8) & 0xff, h & 0xff


def rgb2hex(r, g, b):
    return (r << 16) + (g << 8) + b


def _get_all_present_colours(im):
    """Returns a dict of RGB colours present.

    N.B. Do not use this except for testing purposes.

    Reference: http://stackoverflow.com/a/4643911

    :param im: The image to get number of colours in.
    :type im: :class:`~PIL.Image.Image`
    :return: A dict of contained RGB colours as keys.
    :rtype: dict

    """
    from collections import defaultdict
    by_color = defaultdict(int)
    for pixel in im.getdata():
        by_color[pixel] += 1
    return by_color


class Palette(object):
    """The :mod:`~hitherdither` implementation of a colour palette.

    Can be instantiated in from colour specifications in the following forms:

    - ``uint8`` numpy array of size ``[N x 3]``
    - ``uint8`` numpy array of size ``[3N]``
    - :class:`~PIL.ImagePalette.ImagePalette`
    - :class:`~PIL.Image.Image`
    - list of hex values
    - list of RGB tuples

    """

    def __init__(self, data):
        if isinstance(data, np.ndarray):
            if data.ndim == 1:
                self.colours = data.reshape((3, len(data) // 3))
            else:
                self.colours = data
            self.hex = [rgb2hex(*colour) for colour in data]
        elif isinstance(data, ImagePalette):
            _tmp = np.frombuffer(data.palette, 'uint8')
            self.colours = _tmp.reshape((3, len(_tmp) // 3))
            self.hex = [rgb2hex(*colour) for colour in data]
        elif isinstance(data, Image.Image):
            if data.palette is None:
                raise PaletteCouldNotBeCreatedError(
                    "Image of mode {0} has no PIL palette. "
                    "Make sure it is of mode P.".format(data.mode))
            _colours = data.getcolors()
            _n_colours = len(_colours)
            _tmp = np.array(data.getpalette())[:3 * _n_colours]
            self.colours = _tmp.reshape((3, len(_tmp) // 3)).T
            self.hex = [rgb2hex(*colour) for colour in self]
        elif isinstance(data, (list, tuple)):
            if isinstance(data[0], string_type):
                # Assume hex strings
                self.hex = data
                self.colours = np.array([hex2rgb(c) for c in data])
            elif isinstance(data[0], int):
                # Assume hex values
                self.hex = data  # TODO: Convert to hex string.
                self.colours = np.array([hex2rgb(c) for c in data])
            else:
                # Assume RGB tuples
                self.colours = np.array(data)
                self.hex = [rgb2hex(*colour) for colour in data]

    def __iter__(self):
        for colour in self.colours:
            yield colour

    def __len__(self):
        return self.colours.shape[0]

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.colours[item, :]
        else:
            raise IndexError("Can only reference colours by integer values.")

    def render(self, colours):
        return np.array(np.take(self.colours, colours, axis=0), 'uint8')

    def image_distance(self, image, order=2):
        ni = np.array(image, 'float')
        distances = np.zeros((ni.shape[0], ni.shape[1], len(self)), 'float')
        for i, colour in enumerate(self):
            distances[:, :, i] = np.linalg.norm(ni - colour, ord=order, axis=2)
        return distances

    def image_closest_colour(self, image, order=2):
        return np.argmin(self.image_distance(image, order=order), axis=2)

    def pixel_distance(self, pixel, order=2):
        return np.array([np.linalg.norm(pixel - colour, ord=order)
                         for colour in self])

    def pixel_closest_colour(self, pixel, order=2):
        return self.colours[np.argmin(
            self.pixel_distance(pixel, order=order)), :].copy()

    @classmethod
    def create_by_kmeans(cls, image):
        raise NotImplementedError()

    @classmethod
    def create_by_median_cut(cls, image, n=16, dim=None):
        img = np.array(image)
        # Create pixel buckets to simplify sorting and splitting.
        if img.ndim == 3:
            pixels = img.reshape((img.shape[0] * img.shape[1], img.shape[2]))
        elif img.ndim == 2:
            pixels = img.reshape((img.shape[0] * img.shape[1], 1))

        def median_cut(p, dim=None):
            """Median cut method.

            Reference:
            https://en.wikipedia.org/wiki/Median_cut

            :param p: The pixel array to split in two.
            :return: Two numpy arrays, split by median cut method.
            """
            if dim is not None:
                sort_dim = dim
            else:
                mins = p.min(axis=0)
                maxs = p.max(axis=0)
                sort_dim = np.argmax(maxs - mins)

            argument = np.argsort(p[:, sort_dim])
            p = p[argument, :]
            m = np.median(p[:, sort_dim])
            split_mask = p[:, sort_dim] >= m
            return [p[~split_mask, :].copy(), p[split_mask, :].copy()]

        # Do actual splitting loop.
        bins = [pixels, ]
        while len(bins) < n:
            new_bins = []
            for bin in bins:
                new_bins += median_cut(bin, dim)
            bins = new_bins

        # Average over pixels in each bin to create
        colours = np.array([np.array(bin.mean(axis=0).round(), 'uint8')
                            for bin in bins], 'uint8')
        return cls(colours)

    def create_PIL_png_from_closest_colour(self, cc):
        """Create a ``P`` PIL image with this palette.

        Avoids the PIL dithering in favour of our own.

        Reference: http://stackoverflow.com/a/29438149

        :param :class:`numpy.ndarray` cc: A ``[M x N]`` array with integer
            values representing palette colour indices to build image from.
        :return: A :class:`PIL.Image.Image` image of mode ``P``.

        """
        pa_image = Image.new("P", cc.shape[::-1])
        pa_image.putpalette(self.colours.flatten().tolist())
        im = Image.fromarray(np.array(cc, 'uint8')).im.convert(
            "P", 0, pa_image.im)
        try:
            # Pillow >= 4
            return pa_image._new(im)
        except AttributeError:
            # Pillow < 4
            return pa_image._makeself(im)

    def create_PIL_png_from_rgb_array(self, img_array):
        """Create a ``P`` PIL image from a RGB image with this palette.

        Avoids the PIL dithering in favour of our own.

        Reference: http://stackoverflow.com/a/29438149

        :param :class:`numpy.ndarray` img_array: A ``[M x N x 3]`` uint8
            array representing RGB colours.
        :return: A :class:`PIL.Image.Image` image of mode ``P`` with colours
            available in this palette.

        """
        cc = self.image_closest_colour(img_array, order=2)
        pa_image = Image.new("P", cc.shape[::-1])
        pa_image.putpalette(self.colours.flatten().tolist())
        im = Image.fromarray(np.array(cc, 'uint8')).im.convert(
            "P", 0, pa_image.im)
        try:
            # Pillow >= 4
            return pa_image._new(im)
        except AttributeError:
            # Pillow < 4
            return pa_image._makeself(im)

    @staticmethod
    def hex2rgb(x):
        return hex2rgb(x)

    @staticmethod
    def rgb2hex(r, g, b):
        return rgb2hex(r, g, b)
