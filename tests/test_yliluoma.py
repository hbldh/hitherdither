# -*- coding: utf-8 -*-
import numpy as np
import pytest
from PIL import Image

from hitherdither.ordered.yliluoma import yliluomas_1_ordered_dithering
from hitherdither.ordered.yliluoma import _algorithm_one as a1
from hitherdither.palette import Palette


def _pal():
    return Palette([(0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 0, 255)])


@pytest.mark.parametrize("order", [2, 4, 8])
def test_mixing_plan_matches_order(order):
    mix, plans, dist = a1._get_mixing_plan_matrix(_pal(), order)
    # 4 solid colours + 6 pairs * order**2 ratios.
    n = 4 + 6 * order * order
    assert len(mix) == len(plans) == len(dist) == n
    assert max(p[2] for p in plans) < 1.0


def test_plans_index_based_with_rgb_collisions():
    # Duplicate palette colours give identical mixed RGBs; each row must still
    # have its own plan.
    pal = Palette([(0, 0, 0), (0, 0, 0), (255, 255, 255)])
    mix, plans, _ = a1._get_mixing_plan_matrix(pal, 2)
    assert len(plans) == len(mix)
    assert len(set(map(tuple, mix.tolist()))) < len(mix)


@pytest.mark.parametrize("order", [2, 4, 8])
def test_yliluoma_runs_all_orders(order):
    rng = np.random.RandomState(0)
    img = Image.fromarray(rng.randint(0, 256, (8, 8, 3)).astype("uint8"))
    out = yliluomas_1_ordered_dithering(img, _pal(), order=order)
    assert out.mode == "P" and out.size == (8, 8)
    assert np.array(out).max() < 4


def test_yliluoma_solid_colours_preserved():
    for i, c in enumerate(_pal().colours.tolist()):
        img = Image.fromarray(np.full((8, 8, 3), c, "uint8"))
        out = yliluomas_1_ordered_dithering(img, _pal(), order=4)
        assert (np.array(out) == i).all()


def test_yliluoma_grey_gradient_monotonic():
    pal = Palette([(0, 0, 0), (255, 255, 255)])
    row = np.linspace(0, 255, 32).astype("uint8")
    img = Image.fromarray(np.tile(row[None, :, None], (8, 1, 3)))
    out = np.array(yliluomas_1_ordered_dithering(img, pal, order=4)) == 1
    blocks = out.mean(axis=0).reshape(4, -1).mean(axis=1)
    assert np.all(np.diff(blocks) >= -1e-9) and blocks[-1] > blocks[0]
