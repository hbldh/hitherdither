# -*- coding: utf-8 -*-
"""Tests for :mod:`hitherdither.diffusion`."""

import numpy as np
import pytest
from PIL import Image

import hitherdither
from hitherdither.diffusion import _DIFFUSION_MAPS, error_diffusion_dithering

BW = hitherdither.palette.Palette([(0, 0, 0), (255, 255, 255)])


def _bw_array(img):
    return np.array(img.convert("L")) > 127


def _pil_bw(rgb):
    return np.array(rgb.convert("1")) > 0


def _pct_diff(a, b):
    return 100.0 * np.mean(a != b)


def _gradient(w=16, h=16):
    g = np.tile(np.linspace(0, 255, w).astype("uint8"), (h, 1))
    return Image.fromarray(np.stack([g, g, g], axis=2), "RGB")


def test_weights_sum_to_one():
    for name, m in _DIFFUSION_MAPS.items():
        total = sum(w for _, _, w in m)
        if name == "atkinson":
            assert total == pytest.approx(6 / 8)
        else:
            assert total == pytest.approx(1.0), name


def test_stevenson_arce_weights():
    m = _DIFFUSION_MAPS["stevenson-arce"]
    assert sum(w * 200 for _, _, w in m) == pytest.approx(200)
    assert len(m) == 12


@pytest.mark.parametrize("method", sorted(_DIFFUSION_MAPS))
def test_methods_run(method):
    out = error_diffusion_dithering(_gradient(12, 8), BW, method=method)
    assert out.mode == "P"
    assert out.size == (12, 8)


def test_method_case_insensitive():
    out = error_diffusion_dithering(_gradient(6, 4), BW, method="Floyd-Steinberg")
    assert out.mode == "P"


@pytest.mark.parametrize("method", [None, "nope", 3])
def test_invalid_method(method):
    with pytest.raises(ValueError) as e:
        error_diffusion_dithering(_gradient(4, 4), BW, method=method)
    assert "floyd-steinberg" in str(e.value)


def test_grey128_checkerboard_matches_pil():
    """Issue #10."""
    im = Image.new("RGB", (16, 16), (128, 128, 128))
    ours = _bw_array(error_diffusion_dithering(im, BW))
    pil = _pil_bw(im)
    # Uniform checkerboard: every pixel differs from its right neighbour.
    assert np.all(ours[:, 1:] != ours[:, :-1])
    assert np.all(ours[1:, :] != ours[:-1, :])
    # Same checkerboard as PIL, up to phase.
    assert _pct_diff(ours, pil) in (0.0, 100.0)
    assert ours.sum() == 128


@pytest.mark.parametrize("mode", ["L", "1", "RGBA", "P", "CMYK"])
def test_non_rgb_modes(mode):
    im = _gradient(8, 8).convert(mode)
    out = error_diffusion_dithering(im, BW)
    assert out.mode == "P"
    assert out.size == (8, 8)


def test_2d_array():
    out = error_diffusion_dithering(np.full((6, 6), 128, "uint8"), BW)
    assert out.mode == "P"
    assert out.size == (6, 6)


def test_pil_match_report():
    """Prints how closely results match PIL for other levels (informational)."""
    for level in (64, 128, 192):
        im = Image.new("RGB", (16, 16), (level,) * 3)
        d = _pct_diff(_bw_array(error_diffusion_dithering(im, BW)), _pil_bw(im))
        print("grey", level, "differs %.1f%%" % d)
    g = _gradient()
    d = _pct_diff(_bw_array(error_diffusion_dithering(g, BW)), _pil_bw(g))
    print("gradient differs %.1f%%" % d)
