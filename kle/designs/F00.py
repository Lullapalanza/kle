"""
Flip-chip test 0
"""

from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape
from kle.layout.dot_elements import (
    get_Lazar_global_markers,
    get_dot_with_leads, DotWLeadsParams,
    get_andreev_dot_with_loop, ADParams,
)
from kle.layout.layout_connections import ConnectedElement


LAYER_NAMES = [
    "-CHIP",
    "METAL_0",
    "CHIP_TOP",
    "METAL_TOP" 
]

layout = KleLayout(10000, 10000, LAYER_NAMES)
layers = layout.get_layers()

top_chip = KleLayoutElement()
top_chip.add_element(create_shape(layers["CHIP_TOP"], [
    [0, 0], [0, 6000], [6000, 6000], [6000, 0]
]).move(2000, 2000))

layout.add_element(top_chip)


pads = KleLayoutElement()
def get_double_pad(width):
    dpad = KleLayoutElement()
    points = [[0, 0], [width, 0], [width, width], [0, width]]
    dpad.add_element(create_shape(layers["METAL_0"], points))
    dpad.add_element(create_shape(layers["METAL_TOP"], points))
    return dpad


for i, w in enumerate([600, 500, 400, 300, 200, 150, 100]):
    dpad = get_double_pad(w)
    dpad.move(2000 + 500, 2000 + 500 + 800 * i)
    pads.add_element(dpad)

layout.add_element(pads)
layout.add_element(pads.get_copy().flip_vertically().move(5000, 5000).flip_horizontally())


center_pad = KleLayoutElement()
points = [[0, 0], [1000, 0], [1000, 1000], [0, 1000]]
center_pad.add_element(create_shape(layers["METAL_0"], points))
center_pad.add_element(create_shape(layers["METAL_TOP"], points))

layout.add_element(center_pad.get_copy().move(3700, 3700))
layout.add_element(center_pad.get_copy().move(5300, 3700))
layout.add_element(center_pad.get_copy().move(5300, 5300))
layout.add_element(center_pad.get_copy().move(3700, 5300))


layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/F00_20250128.gds"
)
