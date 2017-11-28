#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import pathlib2 as pathlib
except ImportError:
    import pathlib

try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen

from PIL import Image


def scene():
    """Chrono Cross PNG image used in Yliluoma's web page.

    :return: The PIL image of the Chrono Cross scene.

    """
    image_path = pathlib.Path(__file__).resolve().parent.joinpath('scene.png')
    image_url = "http://bisqwit.iki.fi/jutut/kuvat/ordered_dither/scene.png"
    return _image(image_path, image_url)


def scene_undithered():
    """Chrono Cross PNG image rendered directly with specified palette.

    :return: The PIL image of the undithered Chrono Cross scene.

    """
    return _image(
        pathlib.Path(__file__).resolve().parent.joinpath('scenenodither.png'),
        "http://bisqwit.iki.fi/jutut/kuvat/ordered_dither/scenenodither.png")


def scene_bayer0():
    """Chrono Cross PNG image dithered using ordered Bayer matrix method.

    :return: The PIL image of the ordered Bayer matrix dithered
        Chrono Cross scene.

    """
    return _image(
        pathlib.Path(__file__).resolve().parent.joinpath('scenebayer0.png'),
        "http://bisqwit.iki.fi/jutut/kuvat/ordered_dither/scenebayer0.png"
    )


def _image(pth, url):
    """Load image specified in ``path``. If not present,
    fetch it from ``url`` and store locally.

    :param str or :class:`~pathlib.Path` pth:
    :param str url: URL from where to fetch the image.
    :return: The :class:`~PIL.Image` requested.

    """
    if pth.exists():
        return Image.open(str(pth))
    else:
        r = urlopen(url)
        with open(str(pth), 'wb') as f:
            f.write(r.read())
        return _image(pth, url)


def palette():
    return [0x080000, 0x201A0B, 0x432817, 0x492910,
            0x234309, 0x5D4F1E, 0x9C6B20, 0xA9220F,
            0x2B347C, 0x2B7409, 0xD0CA40, 0xE8A077,
            0x6A94AB, 0xD5C4B3, 0xFCE76E, 0xFCFAE2]
