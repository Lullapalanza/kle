"""
Ansys test file
"""
from kle.layout.layout import KleLayout, KleLayoutElement, KleShape
from kle.layout.dot_elements import (
    get_circle_points,
    get_sensor_dot
)


LA_LAYERS = ["G0", "G1", "O"] # Local alignment layers, gate, ohmics
def get_layers_for_la(id):
    """
    layer names for local alignment
    """
    return [
        f"{la_layer}_{id}" for la_layer in LA_LAYERS
    ]

LAYER_NAMES = [
    "-CHIP",
    "MARKERS",
    "BC", # Barriers Corse
    "BPC", # Bond Pads circles
    "TS_B", # Test structure barrier
    "TS_G", # TS gate
    "TS_O", # TS ohmics
]

for lid in [0, 1, 2, 3, 4, 5]:
    LAYER_NAMES.extend(get_layers_for_la(lid))

layout = KleLayout(6000, 6000, LAYER_NAMES)
layers = layout.get_layers()

# 
marker_quadrant = KleLayoutElement("marker quadrant")

# Make one global marker cross
g_marker = KleLayoutElement("Global marker")

m_largearm_shape = KleShape(layers["MARKERS"], [(0, -2.5), (84, -2.5), (84, 2.5), (0, 2.5)])
g_marker.add_element(m_largearm_shape.get_copy())
g_marker.add_element(m_largearm_shape.get_copy().move(84 + 12, 0))
g_marker.add_element(m_largearm_shape.get_copy().rotate_left().move(84 + 6, 6))
g_marker.add_element(m_largearm_shape.get_copy().rotate_left().move(84 + 6, -84 - 6))

m_smallarm_shape = KleShape(layers["MARKERS"], [(-5, -0.25), (5, -0.25), (5, 0.25), (-5, 0.25)])
g_marker.add_element(m_smallarm_shape.get_copy().move(90, 0))
g_marker.add_element(m_smallarm_shape.get_copy().rotate_left().move(90, 0))

marker_quadrant.add_element(g_marker.get_copy())
marker_quadrant.add_element(g_marker.get_copy().move(200, 0))
layout.add_element(marker_quadrant)


layout.build()
layout.save_gds("C:/Users/nbr720/Documents/PhD/design/gds_files/AQ00_20240815.dxf")