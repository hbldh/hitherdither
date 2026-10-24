#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`test_palette`
=======================

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>
Created on 2016-09-13, 09:38

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import pytest
import numpy as np
from PIL import Image

from hitherdither import palette
from hitherdither.exceptions import PaletteCouldNotBeCreatedError
from hitherdither.data import scene, scene_bayer0, scene_undithered


@pytest.mark.parametrize(
    "hex_colour, rgb_colour",
    (
        ("#ffffff", (255, 255, 255)),
        ("#abcdef", (171, 205, 239)),
        ("#012345", (1, 35, 69)),
        (0x82F698, (130, 246, 152)),
        ("0x82f698", (130, 246, 152)),
    ),
)
def test_hex2rgb(hex_colour, rgb_colour):
    assert palette.hex2rgb(hex_colour) == rgb_colour


@pytest.mark.parametrize(
    "hex_colour, rgb_colour",
    (
        ("#ffffff", (255, 255, 255)),
        ("#abcdef", (171, 205, 239)),
        ("#012345", (1, 35, 69)),
        (0x82F698, (130, 246, 152)),
        ("0x82f698", (130, 246, 152)),
    ),
)
def test_rgb2hex(hex_colour, rgb_colour):
    try:
        if isinstance(hex_colour, int):
            hc = hex_colour
        else:
            hc = int(hex_colour, 16)
    except:
        hc = int(hex_colour[1:], 16)
    assert palette.rgb2hex(*rgb_colour) == hc


@pytest.mark.parametrize(
    "input_data, n_colours",
    (
        (
            [
                np.array((255, 255, 255)),
                np.array((171, 205, 239)),
                np.array((1, 35, 69)),
                np.array((130, 246, 152)),
            ],
            4,
        ),
        ([(255, 255, 255), (171, 205, 239), (1, 35, 69), (130, 246, 152)], 4),
        (
            np.array(
                [
                    (255, 255, 255),
                    (171, 205, 239),
                    (1, 35, 69),
                    (130, 246, 152),
                    (0, 0, 0),
                ]
            ),
            5,
        ),
        (
            [
                "#ff21ee",
                "#123456",
                "#abcdef",
                "#000000",
            ],
            4,
        ),
        (
            [
                0xFF21EE,
                0x123456,
                0xABCDEF,
                0x000000,
            ],
            4,
        ),
    ),
)
def test_create(input_data, n_colours):
    p = palette.Palette(input_data)
    if isinstance(n_colours, tuple):
        # JPEG gets 80 colours in Python 2.7.9 and 3.4,
        # 82 in Python 2.7.12 and 3.5, 3.6...
        assert len(p) in n_colours
        assert len([c for c in p]) in n_colours
    else:
        assert len(p) == n_colours
        assert len([c for c in p]) == n_colours


def test_create_png(test_png):
    n_colours = 104
    p = palette.Palette(test_png.convert("P"))
    if isinstance(n_colours, tuple):
        # JPEG gets 80 colours in Python 2.7.9 and 3.4,
        # 82 in Python 2.7.12 and 3.5, 3.6...
        assert len(p) in n_colours
        assert len([c for c in p]) in n_colours
    else:
        assert len(p) == n_colours
        assert len([c for c in p]) == n_colours


def test_create_jpg(test_jpeg):
    n_colours = (80, 82)
    p = palette.Palette(test_jpeg.convert("P"))
    if isinstance(n_colours, tuple):
        # JPEG gets 80 colours in Python 2.7.9 and 3.4,
        # 82 in Python 2.7.12 and 3.5, 3.6...
        assert len(p) in n_colours
        assert len([c for c in p]) in n_colours
    else:
        assert len(p) == n_colours
        assert len([c for c in p]) == n_colours


def test_create_bayer0():
    n_colours = 16
    p = palette.Palette(scene_bayer0())
    if isinstance(n_colours, tuple):
        # JPEG gets 80 colours in Python 2.7.9 and 3.4,
        # 82 in Python 2.7.12 and 3.5, 3.6...
        assert len(p) in n_colours
        assert len([c for c in p]) in n_colours
    else:
        assert len(p) == n_colours
        assert len([c for c in p]) == n_colours


def test_create_bayer0():
    n_colours = 16
    p = palette.Palette(scene_undithered())
    if isinstance(n_colours, tuple):
        # JPEG gets 80 colours in Python 2.7.9 and 3.4,
        # 82 in Python 2.7.12 and 3.5, 3.6...
        assert len(p) in n_colours
        assert len([c for c in p]) in n_colours
    else:
        assert len(p) == n_colours
        assert len([c for c in p]) == n_colours


def test_create_fails_1(test_png):
    with pytest.raises(PaletteCouldNotBeCreatedError):
        p = palette.Palette(test_png)


def test_create_fails_2(test_jpeg):
    with pytest.raises(PaletteCouldNotBeCreatedError):
        p = palette.Palette(test_jpeg)


def test_create_fails_3(test_jpeg):
    with pytest.raises(PaletteCouldNotBeCreatedError):
        p = palette.Palette(test_jpeg.convert("L"))


def test_create_fails_4(test_jpeg):
    with pytest.raises(PaletteCouldNotBeCreatedError):
        p = palette.Palette(scene())


def test_median_cut_flat_white():
    im = Image.new("RGB", (10, 10), (255, 255, 255))
    p = palette.Palette.create_by_median_cut(im, n=16)
    assert len(p) == 1
    assert p.colours.shape == (1, 3)
    assert tuple(p.colours[0]) == (255, 255, 255)


def test_median_cut_two_colours():
    arr = np.zeros((10, 10, 3), "uint8")
    arr[:, 5:] = (200, 100, 50)
    p = palette.Palette.create_by_median_cut(Image.fromarray(arr), n=16)
    assert len(p) == 2
    assert {tuple(c) for c in p} == {(0, 0, 0), (200, 100, 50)}


def test_median_cut_three_colours():
    arr = np.zeros((9, 9, 3), "uint8")
    arr[:, 3:6] = (200, 100, 50)
    arr[:, 6:] = (10, 250, 30)
    p = palette.Palette.create_by_median_cut(Image.fromarray(arr), n=16)
    assert len(p) == 3
    assert {tuple(c) for c in p} == {(0, 0, 0), (200, 100, 50), (10, 250, 30)}


def test_median_cut_gradient():
    ramp = np.arange(256, dtype="uint8")
    arr = np.stack([np.tile(ramp, (4, 1))] * 3, axis=2)
    p = palette.Palette.create_by_median_cut(Image.fromarray(arr), n=16)
    assert len(p) == 16
    assert p.colours.shape == (16, 3)


def test_median_cut_non_power_of_two():
    ramp = np.arange(256, dtype="uint8")
    arr = np.stack([np.tile(ramp, (4, 1))] * 3, axis=2)
    p = palette.Palette.create_by_median_cut(Image.fromarray(arr), n=10)
    assert len(p) == 10


def test_median_cut_grey_L():
    ramp = np.arange(256, dtype="uint8")
    im = Image.fromarray(np.tile(ramp, (4, 1)), "L")
    p = palette.Palette.create_by_median_cut(im, n=16)
    assert len(p) == 16
    assert p.colours.shape == (16, 3)
    assert np.all(p.colours[:, 0] == p.colours[:, 1])


@pytest.mark.parametrize("mode", ["1", "L", "RGBA", "P"])
def test_median_cut_modes_give_rgb(mode):
    ramp = np.arange(256, dtype="uint8")
    im = Image.fromarray(np.stack([np.tile(ramp, (4, 1))] * 3, axis=2)).convert(mode)
    p = palette.Palette.create_by_median_cut(im, n=4)
    assert p.colours.ndim == 2 and p.colours.shape[1] == 3
    assert 1 <= len(p) <= 4


def test_median_cut_flat_grey_L():
    p = palette.Palette.create_by_median_cut(Image.new("L", (4, 4), 7), n=8)
    assert len(p) == 1
    assert tuple(p.colours[0]) == (7, 7, 7)


def test_create_1d_array_shape():
    p = palette.Palette(np.array([255, 0, 0, 0, 255, 0], "uint8"))
    assert p.colours.shape == (2, 3)
    assert len(p) == 2
    assert tuple(p.colours[1]) == (0, 255, 0)
    assert p.hex == [0xFF0000, 0x00FF00]


def test_create_uint8_array_hex_no_overflow():
    p = palette.Palette(np.array([(255, 255, 255), (1, 2, 3)], "uint8"))
    assert p.hex == [0xFFFFFF, 0x010203]


def test_create_from_imagepalette():
    from PIL.ImagePalette import ImagePalette

    ip = ImagePalette("RGB", bytes([255, 0, 0, 0, 255, 0, 0, 0, 255]))
    p = palette.Palette(ip)
    assert p.colours.shape == (3, 3)
    assert tuple(p.colours[2]) == (0, 0, 255)
    assert p.hex == [0xFF0000, 0x00FF00, 0x0000FF]


def test_create_from_int_list_hex():
    p = palette.Palette([0xFF21EE, 0x000001])
    assert p.hex == [0xFF21EE, 0x000001]
    assert tuple(p.colours[1]) == (0, 0, 1)


def test_pixel_closest_colour_float_and_uint8():
    p = palette.Palette([(0, 0, 0), (255, 255, 255), (200, 0, 0)])
    assert tuple(p.pixel_closest_colour(np.array([10.4, 9.9, 11.0]))) == (0, 0, 0)
    assert tuple(p.pixel_closest_colour(np.array([250.5, 251.0, 249.0]))) == (
        255,
        255,
        255,
    )
    # uint8 pixel must not wrap around when subtracting.
    assert tuple(p.pixel_closest_colour(np.array([5, 5, 5], "uint8"))) == (0, 0, 0)


def test_image_distance_float_input():
    p = palette.Palette([(0, 0, 0), (255, 255, 255)])
    im = np.full((2, 3, 3), 250.7, dtype="float32")
    d = p.image_distance(im)
    assert d.shape == (2, 3, 2)
    assert np.all(p.image_closest_colour(im) == 1)
    im8 = np.full((2, 3, 3), 5, dtype="uint8")
    assert np.all(p.image_closest_colour(im8) == 0)
