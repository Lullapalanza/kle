"""
Ansys test file
"""
from kle.layout.layout import KleLayout, KleLayoutElement, KleShape
from kle.layout.dot_elements import (
    get_sensor_dot
)


layout = KleLayout(2500, 1200, ["sc", "g0", "g1"])
layers = layout.get_layers()

sd0 = get_sensor_dot(layers["sc"], layers["g0"], layers["g1"])
layout.add_element(sd0)

layout.build()
layout.save_gds("C:/Users/nbr720/Documents/PhD/design/gds_files/Q00_20240801.gds")