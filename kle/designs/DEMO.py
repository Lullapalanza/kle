from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape, create_annotation
from kle.layout.dot_elements import (
    get_Lazar_global_markers,
    get_dot_with_leads, DotWLeadsParams,
    get_andreev_dot_with_loop, ADParams,
)
from kle.layout.layout_trace_routing import get_routed_trace
from kle.layout.layout_connections import get_simple_connector, ConnectedElement, get_connector_extention


LAYER_NAMES = [
    "-CHIP",
    "MARKERS",
    "LM0",
    "LM1",
    "LM2",
    "LM3",
    "OHMICS_0",
    "GATES0_0",
    "GATES1_0",
    "ANNOTATIONS"
]

layout = KleLayout(6000, 6000, LAYER_NAMES)
layers = layout.get_layers()


# shape = create_shape(layers["OHMICS_0"], [(0, 0), (0.1, 0), (0.1, 0.2), (0, 0.2)])
# layout.add_element(shape)

# element = KleLayoutElement()
# element.add_element(shape.get_copy())
# element.add_element(shape.get_copy().rotate_by_angle(90))
# layout.add_element(element)

# layout.add_element(get_Lazar_global_markers(layers["MARKERS"]))

# params = DotWLeadsParams()

# ad0 = get_dot_with_leads(
#     layers["OHMICS_0"],
#     layers["GATES0_0"],
#     layers["GATES1_0"],
#     layers["ANNOTATIONS"],
#     params
# )
# ad1 = get_dot_with_leads(
#     layers["OHMICS_0"],
#     layers["GATES0_0"],
#     layers["GATES1_0"],
#     layers["ANNOTATIONS"],
#     params
# )

# ad0.rotate_by_angle(30)

# layout.add_element(ad0)
# layout.add_element(ad1.move(0.1, 0.6))

# ad0.get_connector("TB").connect_to(ad1.get_connector("BB"), layers["GATES1_0"])

layout.build_to_file("C:/Users/nbr720/Documents/PhD/design/design_files/DEMO.dxf")
