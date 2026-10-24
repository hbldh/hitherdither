Algorithms
==========

Error diffusion
---------------

Floyd-Steinberg, Jarvis-Judice-Ninke, Stucki, Burkes, Sierra3, Sierra2,
Sierra-2-4A and Atkinson, selected with the ``method``
argument of :func:`~hitherdither.diffusion.error_diffusion_dithering`.

The implementation is plain Python loops and therefore slow on large images.
The diffused error is rounded down to whole grey levels so that a flat 50 %
grey image gives a clean checkerboard (like PIL's ``convert('1')``, though
with the opposite phase). Exact floating point Floyd-Steinberg preserves mean
brightness marginally better but leaves sparse defects in such patterns.

Ordered dithering
-----------------

:func:`~hitherdither.ordered.bayer.bayer_dithering` and
:func:`~hitherdither.ordered.cluster.cluster_dot_dithering` add
``(matrix - 0.5) * thresholds`` to each pixel and snap to the nearest palette
colour. With small thresholds and a sparse palette only pixels near palette
boundaries change; raise ``thresholds`` for a stronger pattern.

Yliluoma's algorithm 1
----------------------

:func:`~hitherdither.ordered.yliluoma.yliluomas_1_ordered_dithering` mixes two
palette colours per pixel using a Bayer matrix of the given ``order``. Algorithms
2 and 3 are not implemented.

Measured on a 128x89 image with an 8 colour palette
---------------------------------------------------

====================  ========  ===========
algorithm             time (s)  blurred MAE
====================  ========  ===========
no dithering          0.002     6.43
Bayer 8x8             0.003     6.43
Cluster dot 8x8       0.003     6.51
Yliluoma 1            0.29      5.23
Floyd-Steinberg       0.32      4.49
Sierra-2-4A           0.32      4.47
====================  ========  ===========

"Blurred MAE" is the mean absolute difference to the original after a Gaussian
blur (lower looks closer from a distance). Reproduce with ``examples/demo.py``.
