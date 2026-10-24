# -*- coding: utf-8 -*-
import numpy as np
import pytest
from PIL import Image

from hitherdither.ordered import cluster
from hitherdither.palette import Palette

_M = cluster._CLUSTER_DOT_MATRICES


@pytest.mark.parametrize("key", [4, 8, (5, 3)])
def test_cluster_matrix_is_permutation(key):
    m = _M[key]
    n = m.size
    assert sorted(np.round(m.ravel() * n).astype(int).tolist()) == list(range(n))
    assert m.min() >= 0.0 and m.max() < 1.0


def test_cluster_shapes():
    assert _M[4].shape == (4, 4)
    assert _M[8].shape == (8, 8)
    assert _M[(5, 3)].shape == (3, 5)


def _gradient(width=60, height=15):
    row = np.linspace(0, 255, width).astype("uint8")
    return Image.fromarray(np.tile(row[None, :, None], (height, 1, 3)))


@pytest.mark.parametrize("order", [4, 8, (5, 3)])
@pytest.mark.parametrize("thr", [[64] * 3, [256 / 4] * 3, [255] * 3])
def test_cluster_gradient_monotonic(order, thr):
    pal = Palette([(0, 0, 0), (255, 255, 255)])
    out = cluster.cluster_dot_dithering(_gradient(), pal, thr, order=order)
    assert out.size == (60, 15)
    blocks = (np.array(out) == 1).mean(axis=0).reshape(6, -1).mean(axis=1)
    assert np.all(np.diff(blocks) >= -1e-9)
    assert blocks[-1] > blocks[0]


def test_cluster_no_overflow():
    pal = Palette([(0, 0, 0), (255, 255, 255)])
    img = Image.fromarray(np.full((16, 16, 3), 250, "uint8"))
    out = cluster.cluster_dot_dithering(img, pal, [256 / 4] * 3, order=8)
    assert (np.array(out) == 1).all()


def test_cluster_bad_order():
    pal = Palette([(0, 0, 0), (255, 255, 255)])
    with pytest.raises(NotImplementedError):
        cluster.cluster_dot_dithering(_gradient(), pal, [64] * 3, order=3)
