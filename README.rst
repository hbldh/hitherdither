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
    - Atkinson
    - Stevenson-Arce (*experimental*: an adaptation to square pixels of an
      algorithm designed for hexagonal grids, see issue #6)
* Standard ordered dithering
    - Bayer matrix
    - Cluster dot matrix (orders 4, 8 and ``(5, 3)``)
    - Arbitrary square threshold matrix (not implemented yet)
* Yliluoma's ordered dithering (see [1]_)
    - Algorithm 1
    - Algorithm 2 (not implemented yet)
    - Algorithm 3 (not implemented yet)

The algorithms work with arbitrary palettes. Input images of any PIL mode
(``L``, ``1``, ``RGBA``, ``P`` ...) are converted to RGB first, and the result is
a ``P`` mode image using the given palette. Error diffusion is written in
plain Python loops and is slow on large images; resize first.

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

Greyscale and black-and-white images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Images of any PIL mode (``L``, ``1``, ``LA``, ``RGBA``, ``P``, ``CMYK``) and 2-D
arrays are accepted by every algorithm; they are converted to RGB internally.
Use a greyscale palette for a greyscale result:

.. code:: python

   from PIL import Image
   import hitherdither
   from hitherdither.palette import Palette

   img = Image.open('photo.png').convert('L')
   bw = Palette.create_greyscale(2)           # black and white
   grey4 = Palette.create_greyscale(4)        # 0, 85, 170, 255
   custom = Palette.from_greys([0, 96, 255])  # chosen grey levels
   out = hitherdither.diffusion.error_diffusion_dithering(img, bw)

.. note::
   ``Palette([0, 255])`` is a list of *hex colour values* (black and blue),
   not grey levels. Use ``Palette.from_greys`` for grey levels.

Examples
~~~~~~~~

``examples/demo.py`` runs every algorithm on one image, prints runtime and a
quality figure, and writes the results plus ``overview.png`` to
``examples/output/``:

.. code:: sh

    python examples/demo.py                    # generated test picture
    python examples/demo.py photo.jpg --colours 16 --size 256

Typical output (128x89 px, 8-colour median cut palette). "blurred MAE" is the
mean absolute difference to the original after a Gaussian blur, so lower means
it looks closer to the original from a distance:

====================  ========  ============
algorithm             time (s)  blurred MAE
====================  ========  ============
no dithering          0.002     6.43
Bayer 8x8             0.003     6.43
Cluster dot 8x8       0.003     6.51
Yliluoma 1            0.29      5.23
Floyd-Steinberg       0.32      4.49
Atkinson              0.34      4.83
Jarvis-Judice-Ninke   0.41      4.87
Stucki                0.40      4.79
Burkes                0.37      4.55
Sierra3               0.40      4.82
Sierra2               0.35      4.50
Sierra-2-4A           0.32      4.47
Stevenson-Arce        0.41      5.04
====================  ========  ============

Ordered dithering adds ``(matrix - 0.5) * thresholds`` to each pixel, so with
small thresholds on a sparse palette it only changes pixels near palette
boundaries. Increase ``thresholds`` for a stronger pattern.

Tests
~~~~~

Tests can be run with `pytest <http://doc.pytest.org/en/latest/>`_:

.. code:: sh

    pip install -e . pytest
    pytest tests

A few tests in ``tests/test_palette.py`` download example images and fail when
the network or the image URLs are unavailable.

References
----------

.. [1] Joel Yliluoma's arbitrary-palette positional dithering algorithm (http://bisqwit.iki.fi/story/howto/dither/jy/)


.. |Build Status| image:: https://github.com/hbldh/hitherdither/workflows/Build%20and%20Test/badge.svg
   :target: https://github.com/hbldh/hitherdither/actions?query=workflow%3A%22Build+and+Test%22
   :alt: Build and Test
.. |Coverage Status| image:: https://coveralls.io/repos/github/hbldh/hitherdither/badge.svg?branch=master
   :target: https://coveralls.io/github/hbldh/hitherdither?branch=master
