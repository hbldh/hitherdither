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
        return hex2rgb(int(h[1:] if h.startswith("#") else h, 16))
    return (h >> 16) & 0xFF, (h >> 8) & 0xFF, h & 0xFF


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

    .. warning::

        A list of plain integers is interpreted as *hex colour values*, not
        as grey levels: ``Palette([0, 255])`` is black and **blue**
        (``0x0000FF``). For greyscale palettes use :meth:`create_greyscale`
        or :meth:`from_greys`.

    """

    def __init__(self, data):
        if isinstance(data, np.ndarray):
            if data.ndim == 1:
                self.colours = data.reshape((len(data) // 3, 3))
            else:
                self.colours = data
            self.hex = self._colours_to_hex(self.colours)
        elif isinstance(data, ImagePalette):
            _tmp = np.frombuffer(bytes(data.palette), "uint8")
            self.colours = _tmp.reshape((len(_tmp) // 3, 3))
            self.hex = self._colours_to_hex(self.colours)
        elif isinstance(data, Image.Image):
            if data.palette is None:
                raise PaletteCouldNotBeCreatedError(
                    "Image of mode {0} has no PIL palette. "
                    "Make sure it is of mode P.".format(data.mode)
                )
            _colours = data.getcolors()
            _n_colours = len(_colours)
            _tmp = np.array(data.getpalette())[: 3 * _n_colours]
            self.colours = _tmp.reshape((3, len(_tmp) // 3)).T
            self.hex = self._colours_to_hex(self.colours)
        elif isinstance(data, (list, tuple)):
            if isinstance(data[0], string_type):
                # Assume hex strings
                self.hex = data
                self.colours = np.array([hex2rgb(c) for c in data])
            elif isinstance(data[0], (int, np.integer)):
                # Assume hex values
                self.colours = np.array([hex2rgb(int(c)) for c in data])
                self.hex = self._colours_to_hex(self.colours)
            else:
                # Assume RGB tuples
                self.colours = np.array(data)
                self.hex = self._colours_to_hex(self.colours)

    @staticmethod
    def _colours_to_hex(colours):
        # Cast to Python ints to avoid fixed-width integer overflow when shifting.
        return [rgb2hex(*(int(v) for v in colour)) for colour in colours]

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
        return np.array(np.take(self.colours, colours, axis=0), "uint8")

    def image_distance(self, image, order=2):
        ni = np.array(image, "float")
        distances = np.zeros((ni.shape[0], ni.shape[1], len(self)), "float")
        for i, colour in enumerate(self):
            distances[:, :, i] = np.linalg.norm(
                ni - np.asarray(colour, dtype="float"), ord=order, axis=2
            )
        return distances

    def image_closest_colour(self, image, order=2):
        return np.argmin(self.image_distance(image, order=order), axis=2)

    def pixel_distance(self, pixel, order=2):
        pixel = np.asarray(pixel, dtype="float")
        return np.array(
            [
                np.linalg.norm(pixel - np.asarray(colour, dtype="float"), ord=order)
                for colour in self
            ]
        )

    def pixel_closest_colour(self, pixel, order=2):
        return self.colours[
            np.argmin(self.pixel_distance(pixel, order=order)), :
        ].copy()

    @classmethod
    def from_greys(cls, levels):
        """Create a greyscale palette from grey levels.

        ``Palette.from_greys([0, 255])`` is a black and white palette.

        :param levels: Iterable of grey levels, integers in ``[0, 255]``.
        :return: A :class:`Palette` with one ``(g, g, g)`` colour per level.
        """
        levels = [int(v) for v in levels]
        if len(levels) == 0:
            raise ValueError("At least one grey level is required.")
        if any(v < 0 or v > 255 for v in levels):
            raise ValueError("Grey levels must be in the range [0, 255].")
        return cls(np.array([[v, v, v] for v in levels], "uint8"))

    @classmethod
    def create_greyscale(cls, n=2):
        """Create a palette of ``n`` evenly spaced greys from black to white.

        ``create_greyscale(2)`` is black and white, ``create_greyscale(4)``
        gives 0, 85, 170 and 255.

        :param int n: Number of grey levels, at least 2 (at most 256).
        """
        if int(n) != n or n < 2 or n > 256:
            raise ValueError("n must be an integer in the range [2, 256].")
        n = int(n)
        return cls.from_greys(np.round(np.linspace(0, 255, n)).astype(int))

    @classmethod
    def create_by_kmeans(cls, image):
        raise NotImplementedError()

    @classmethod
    def create_by_median_cut(cls, image, n=16, dim=None):
        """Create a palette with (at most) ``n`` colours by median cut.

        Images of mode other than ``RGB`` (``L``, ``1``, ``P``, ``RGBA``, ...)
        are converted to ``RGB`` first, so the resulting palette is always
        of shape ``[N x 3]``. If the image contains fewer than ``n`` distinct
        colours, a palette with fewer than ``n`` colours is returned.

        :param image: The image (PIL image or array) to create palette from.
        :param int n: Maximum number of colours in the palette.
        :param int dim: Colour channel to always split along. Default is
            the channel with the largest range in each bin.
        """
        if isinstance(image, Image.Image):
            if image.mode != "RGB":
                image = image.convert("RGB")
            img = np.array(image)
        else:
            img = np.array(image)
            if img.ndim == 2:
                img = np.stack([img] * 3, axis=2)
            elif img.ndim == 3 and img.shape[2] == 1:
                img = np.repeat(img, 3, axis=2)
            elif img.ndim == 3 and img.shape[2] == 4:
                img = img[:, :, :3]
        pixels = img.reshape((-1, img.shape[-1]))

        def split_dim(p):
            """Channel to split ``p`` along, or None if it cannot be split."""
            if len(p) < 2:
                return None
            ranges = p.max(axis=0).astype(int) - p.min(axis=0).astype(int)
            if dim is not None:
                return dim if ranges[dim] > 0 else None
            d = int(np.argmax(ranges))
            return d if ranges[d] > 0 else None

        def median_cut(p, sort_dim):
            """Median cut method.

            Reference:
            https://en.wikipedia.org/wiki/Median_cut

            :param p: The pixel array to split in two (non-empty halves).
            :param sort_dim: The channel to split along; must have range > 0.
            :return: Two numpy arrays, split by median cut method.
            """
            m = np.median(p[:, sort_dim])
            split_mask = p[:, sort_dim] >= m
            if split_mask.all():
                # Median equals minimum value: split off the minimum instead.
                split_mask = p[:, sort_dim] > m
            return [p[~split_mask, :].copy(), p[split_mask, :].copy()]

        # Do actual splitting loop.
        bins = [pixels]
        while len(bins) < n:
            new_bins = []
            did_split = False
            for i, b in enumerate(bins):
                # Total bins if this one were split; never exceed n.
                total = len(new_bins) + (len(bins) - i) + 1
                d = split_dim(b) if total <= n else None
                if d is None:
                    new_bins.append(b)
                else:
                    new_bins += median_cut(b, d)
                    did_split = True
            bins = new_bins
            if not did_split:
                break

        # Average over pixels in each bin to create the palette colours.
        colours = np.array(
            [np.array(b.mean(axis=0).round(), "uint8") for b in bins], "uint8"
        )
        return cls(colours)

    def create_PIL_png_from_closest_colour(self, cc):
        """Create a ``P`` PIL image with this palette.

        Avoids the PIL dithering in favour of our own.

        Reference: http://stackoverflow.com/a/29438149

        :param cc: A ``[M x N]`` array with integer
            values representing palette colour indices to build image from.
        :return: A :class:`PIL.Image.Image` image of mode ``P``.

        """
        pa_image = Image.fromarray(np.array(cc, "uint8"), "P")
        pa_image.putpalette(np.asarray(self.colours, "uint8").flatten().tolist())
        return pa_image

    def create_PIL_png_from_rgb_array(self, img_array):
        """Create a ``P`` PIL image from a RGB image with this palette.

        Avoids the PIL dithering in favour of our own.

        Reference: http://stackoverflow.com/a/29438149

        :param img_array: A ``[M x N x 3]`` uint8
            array representing RGB colours.
        :return: A :class:`PIL.Image.Image` image of mode ``P`` with colours
            available in this palette.

        """
        cc = self.image_closest_colour(img_array, order=2)
        pa_image = Image.fromarray(np.array(cc, "uint8"), "P")
        pa_image.putpalette(np.asarray(self.colours, "uint8").flatten().tolist())
        return pa_image

    @staticmethod
    def hex2rgb(x):
        return hex2rgb(x)

    @staticmethod
    def rgb2hex(r, g, b):
        return rgb2hex(r, g, b)
