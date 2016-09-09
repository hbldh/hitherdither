hitherdither
============

|Build Status| |Coverage Status|

Dithering algorithms that is applicable for arbitrary palettes.

Description
-----------

This module is a small extension to `Pillow <https://pillow.readthedocs.io/en/3.3.x/>`_.

Installation
------------

::

    pip install git+https://www.github.com/hbldh/hitherdither

Usage
-----

.. code:: python

   from PIL import Image
   import hitherdither

   img = Image.open('image.png')
   img_dithered = hitherdither.dither(img)

Tests
~~~~~

Tests can be run with `pytest <http://doc.pytest.org/en/latest/>`_:

.. code:: sh

   Testing started at 13:28 ...
   ============================= test session starts ==============================
   platform linux2 -- Python 2.7.12, pytest-3.0.1, py-1.4.31, pluggy-0.3.1
   rootdir: /home/hbldh/Repos/hitherdither, inifile:
   collected 0 items

   =========================== 0 passed in 0.00 seconds ===========================

References
----------

.. [1] Joel Yliluoma's arbitrary-palette positional dithering algorithm (http://bisqwit.iki.fi/story/howto/dither/jy/)

.. [2] Exif orientation (http://sylvana.net/jpegcrop/exif_orientation.html)


.. |Build Status| image:: https://travis-ci.org/hbldh/hitherdither.svg?branch=master
   :target: https://travis-ci.org/hbldh/hitherdither
.. |Coverage Status| image:: https://coveralls.io/repos/github/hbldh/hitherdither/badge.svg?branch=master
   :target: https://coveralls.io/github/hbldh/hitherdither?branch=master
