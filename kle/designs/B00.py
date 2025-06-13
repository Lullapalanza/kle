"""
Design for Bertram and rasmus for dots coupled to Bertram designed current control

heidelberg
marks_RestoRas08.gds reference for markers
notebook there as well
1 and 2 gates/dots
1Ghz BiasT like filter (2pads)

10x10 chip
"""
from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape, KleCutOut, create_ref
from kle.layout.dot_elements import (
    get_Lazar_global_markers,
    get_dot_with_leads, DotWLeadsParams,
    get_andreev_dot_with_loop, ADParams,
)
from kle.layout.resonator_elements import get_resonator_LC, get_coplanar_C, get_cpw_port, get_interdigit_LC, get_L_length, LCParams, get_cpw_impedance
from kle.layout.layout_trace_routing import get_routed_cpw, get_routed_trace
from kle.layout.layout_connections import ConnectedElement



LSHEET = 63e-12 # 63 ph/sq
EPS = 11.7

LAYER_NAMES = [
    "SC",
]
layout = KleLayout(6000, 6000, LAYER_NAMES)
layers = layout.get_layers()

# === START BORDER ===
border_shape = create_shape(layers["SC"], [
    [200, 200], [7800, 200], [7800, 300], [200, 300]
])
layout.add_element(border_shape)
layout.add_element(border_shape.get_copy().move(0, 7500))
layout.add_element(border_shape.get_copy().rotate_right().move(0, 8000))
layout.add_element(border_shape.get_copy().rotate_right().move(7500, 8000))

# === END BORDER ===


layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/B00_63pH_11_7eps_20250613.gds"
)