Quickstart
==========

Installation
------------

.. code-block:: sh

   pip install git+https://github.com/hbldh/hitherdither

Dither with a median cut palette
--------------------------------

.. code-block:: python

   from PIL import Image
   import hitherdither

   img = Image.open("image.jpg")
   palette = hitherdither.palette.Palette.create_by_median_cut(img, n=8)
   out = hitherdither.diffusion.error_diffusion_dithering(img, palette, "floyd-steinberg")
   out.save("dithered.png")

Greyscale and black-and-white
-----------------------------

Every algorithm accepts any PIL mode and converts it to RGB internally. Use a
greyscale palette for a greyscale result:

.. code-block:: python

   bw = hitherdither.palette.Palette.create_greyscale(2)
   out = hitherdither.ordered.bayer.bayer_dithering(img, bw, [64, 64, 64], order=8)

.. warning::
   ``Palette([0, 255])`` is a list of *hex colour values* (black and blue), not
   grey levels. Use :meth:`~hitherdither.palette.Palette.from_greys` for grey
   levels.

Try all algorithms
------------------

``examples/demo.py`` in the repository runs every algorithm on an image, prints
the runtime of each and a quality figure, and writes a contact sheet:

.. code-block:: sh

   python examples/demo.py photo.jpg --colours 16 --size 256
