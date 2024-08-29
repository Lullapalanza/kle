"""
Test resonator elements
"""
from kle.layout.layout import KleLayout, KleLayoutElement, create_shape
from kle.layout.resonator_elements import (
    get_cpw_port
)
from kle.layout.layout_trace_routing import (
    get_routed_cpw,
    get_routed_trace,
)


layout = KleLayout(7000, 7000, ["-neg", "pos"])
layers = layout.get_layers()

port0 = get_cpw_port(layers["neg"], 6, 3, taper_length=60)
layout.add_element(port0.move(-port0.get_bounding_box()[0][0], 6500))

port1 = get_cpw_port(layers["pos"], 4, 3)
layout.add_element(port1.move(-port1.get_bounding_box()[0][0], 6200))

cpw0 = get_routed_cpw(layers["neg"], width=7, gap=4, path=[
    (0, 0),
    (100, 0),
    (100, 100)
])
layout.add_element(cpw0.move(200, 200))

cpw1 = get_routed_cpw(layers["pos"], width=7, gap=4, path=[
    (0, 0),
    (100, 0),
    (100, 100)
])
layout.add_element(cpw1.move(400, 200))


ctr0 = get_routed_trace(layers["neg"], [(0, 0), (0, 10), (10, 10)])
layout.add_element(ctr0.move(800, 200))

layout.build_to_file("C:/Users/nbr720/Documents/PhD/design/design_files/TR00.dxf")