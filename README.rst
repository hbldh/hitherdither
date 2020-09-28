hitherdither
============

|Build Status| |Coverage Status|

A package inspired by [1]_, implementing dithering algorithms that can be used with 
`PIL/Pillow <https://pillow.readthedocs.io/en/3.3.x/>`_. 

Description
-----------

This module is a small extension to `PIL/Pillow <https://pillow.readthedocs.io/en/3.3.x/>`_, adding
a more managable palette object and several dithering algorithms:

* Error diffusion dithering
    - Floyd-Steinberg
    - Jarvis-Judice-Ninke
    - Stucki
    - Burkes
    - Sierra3 
    - Sierra2
    - Sierra-2-4A
    - Stevenson-Arce
    - Atkinson
* Standard ordered dithering
    - Bayer matrix
    - Cluster dot matrix
    - Arbitrary square threshold matrix (not implemented yet)
* Yliluoma's ordered dithering (see [1]_)
    - Algorithm 1 
    - Algorithm 2 (not implemented yet)
    - Algorithm 3 (not implemented yet)

The dithering algorithms are applicable for arbitrary palettes and for both
RGB and greyscale images.

Installation
------------

::

    pip install git+https://www.github.com/hbldh/hitherdither

Usage
-----

Bayer dithering using a median cut palette:

.. code:: python

   from PIL import Image
   import hitherdither

   img = Image.open('image.jpg')
   palette = hitherdither.palette.Palette.create_by_median_cut(img)
   img_dithered = hitherdither.ordered.bayer.bayer_dithering(
       img, palette, [256/4, 256/4, 256/4], order=8)

`Yliluoma's Algorithm 1 <http://bisqwit.iki.fi/story/howto/dither/jy/#YliluomaSOrderedDitheringAlgorithm 1>`_
using a predefined palette:

.. code:: python

   from PIL import Image
   import hitherdither

   palette = hitherdither.palette.Palette(
       [0x080000, 0x201A0B, 0x432817, 0x492910,
        0x234309, 0x5D4F1E, 0x9C6B20, 0xA9220F,
        0x2B347C, 0x2B7409, 0xD0CA40, 0xE8A077,
        0x6A94AB, 0xD5C4B3, 0xFCE76E, 0xFCFAE2]
   )

   img = Image.open('image.jpg')
   img_dithered = hitherdither.ordered.yliluoma.yliluomas_1_ordered_dithering(
       img, palette, order=8)

Tests
~~~~~

Tests can be run with `pytest <http://doc.pytest.org/en/latest/>`_:

.. code:: sh

    hbldh@devbox:~/Repos/hitherdither$ py.test tests
    ============================= test session starts ==============================
    platform linux -- Python 3.5.2, pytest-3.0.2, py-1.4.31, pluggy-0.3.1
    rootdir: /home/hbldh/Repos/hitherdither, inifile: 
    collected 13 items 

    tests/test_bayer.py ...
    tests/test_palette.py ..........

    ========================== 13 passed in 0.11 seconds ===========================

References
----------

.. [1] Joel Yliluoma's arbitrary-palette positional dithering algorithm (http://bisqwit.iki.fi/story/howto/dither/jy/)


.. |Build Status| image:: https://github.com/hbldh/hitherdither/workflows/Build%20and%20Test/badge.svg
   :target: https://github.com/hbldh/hitherdither/actions?query=workflow%3A%22Build+and+Test%22
   :alt: Build and Test
.. |Coverage Status| image:: https://coveralls.io/repos/github/hbldh/hitherdither/badge.svg?branch=master
   :target: https://coveralls.io/github/hbldh/hitherdither?branch=master
