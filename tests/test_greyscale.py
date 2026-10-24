# -*- coding: utf-8 -*-
"""Greyscale / non-RGB input handling (GitHub issue #3)."""

import numpy as np
import pytest
from PIL import Image

import hitherdither
from hitherdither.palette import Palette
from hitherdither.ordered.bayer import bayer_dithering
from hitherdither.ordered.cluster import cluster_dot_dithering
from hitherdither.ordered.yliluoma import yliluomas_1_ordered_dithering


def _bayer(im, pal):
    return bayer_dithering(im, pal, [64, 64, 64], order=4)


def _cluster(im, pal):
    return cluster_dot_dithering(im, pal, [64, 64, 64], order=4)


def _yliluoma(im, pal):
    return yliluomas_1_ordered_dithering(im, pal, order=4)


ALGORITHMS = [_bayer, _cluster, _yliluoma]
W, H = 32, 8


def _gradient(mode):
    row = np.linspace(0, 255, W).astype("uint8")
    im = Image.fromarray(np.tile(row, (H, 1)), "L")
    return im.convert(mode)


def test_create_greyscale():
    assert Palette.create_greyscale(2).colours.tolist() == [[0, 0, 0], [255, 255, 255]]
    assert Palette.create_greyscale(4).colours[:, 0].tolist() == [0, 85, 170, 255]
    pal = Palette.create_greyscale(16)
    assert len(pal) == 16
    assert (pal.colours[:, 0] == pal.colours[:, 1]).all()
    assert (pal.colours[:, 0] == pal.colours[:, 2]).all()
    for bad in (0, 1, 257, 2.5):
        with pytest.raises(ValueError):
            Palette.create_greyscale(bad)


def test_from_greys_and_hex_int_list_unchanged():
    assert Palette.from_greys([0, 128, 255]).colours.tolist() == [
        [0, 0, 0], [128, 128, 128], [255, 255, 255]]
    with pytest.raises(ValueError):
        Palette.from_greys([0, 256])
    # Plain int list stays hex: 255 is blue.
    assert Palette([0, 255]).colours.tolist() == [[0, 0, 0], [0, 0, 255]]


@pytest.mark.parametrize("algo", ALGORITHMS)
@pytest.mark.parametrize("mode", ["L", "1", "LA", "RGBA", "P", "CMYK"])
def test_ordered_accepts_any_mode(algo, mode):
    out = algo(_gradient(mode), Palette.create_greyscale(2))
    assert out.mode == "P"
    assert out.size == (W, H)


@pytest.mark.parametrize("algo", ALGORITHMS)
def test_ordered_accepts_2d_array(algo):
    arr = np.tile(np.linspace(0, 255, W).astype("uint8"), (H, 1))
    out = algo(arr, Palette.create_greyscale(2))
    assert out.mode == "P" and out.size == (W, H)


@pytest.mark.parametrize("algo", ALGORITHMS)
def test_ordered_greyscale_gradient_monotone(algo):
    out = algo(_gradient("L"), Palette.create_greyscale(2))
    white = np.array(out.convert("L")).astype(float) > 127
    # Fraction of white pixels per column group rises with brightness.
    frac = [white[:, i:i + 8].mean() for i in range(0, W, 8)]
    assert all(a <= b for a, b in zip(frac, frac[1:]))
    assert frac[0] < frac[-1]


@pytest.mark.parametrize("algo", ALGORITHMS)
def test_black_and_white_stay_pure(algo):
    pal = Palette.create_greyscale(2)
    black = np.array(algo(Image.new("L", (8, 8), 0), pal).convert("L"))
    white = np.array(algo(Image.new("L", (8, 8), 255), pal).convert("L"))
    assert (black == 0).all() and (white == 255).all()
