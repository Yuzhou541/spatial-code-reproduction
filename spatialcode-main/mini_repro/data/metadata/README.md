# Data Notes

`build_object_size_subset.py` generates the evaluation files in `mini_repro/data/`.

The source is a fixed internal bank of 3D scene annotations included in the script. This is intentional: the original paper repository and benchmark extraction code are not available in this workspace, so the mini reproduction uses a controlled object-size benchmark with explicit 3D box metadata.

Ground-truth answers are computed from 3D bounding-box volume:

`volume = x_size * y_size * z_size`

Pairs with size ratio below the ambiguity threshold are filtered out:

`max(volume_a, volume_b) / min(volume_a, volume_b) < 1.10`
