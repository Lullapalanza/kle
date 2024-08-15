"""
Ansys test file
"""
from kle.layout.layout import KleLayout, KleLayoutElement, KleShape
from kle.layout.dot_elements import (
    get_circle_points,
    get_sensor_dot
)


layout = KleLayout(2500, 1200, ["sc", "g0", "g1"])
layers = layout.get_layers()

sd0 = get_sensor_dot(layers["sc"], layers["g0"], layers["g1"], 0.1, 0.125)
layout.add_element(sd0)

sd1 = get_sensor_dot(layers["sc"], layers["g0"], layers["g1"])
# layout.add_element(sd1.move(0.555, 0))
layout.add_element(sd1.move(0.3, 0))


d0 = KleLayoutElement("qd")
DOT_R = 0.120/2
d0.add_element(KleShape(layers["g0"], get_circle_points(DOT_R)))
layout.add_element(d0.move(0.19, 0))


# DOT1
# d1 = KleLayoutElement("qd")
# DOT_R = 0.120/2
# d1.add_element(KleShape(layers["g0"], get_circle_points(DOT_R, 50)))
# layout.add_element(d1.move(0.365, 0))

gs = KleLayoutElement("gates")
barrier = KleShape(layers["g1"], [(0, -0.060), (0.04, -0.060), (0.04, 0.060), (0, 0.060)])
gs.add_element(barrier.get_copy().move(0.0825, 0))
gs.add_element(barrier.get_copy().move(0.0825 + 0.175, 0))
gs.add_element(barrier.get_copy().move(0.0825 + 0.350, 0))
layout.add_element(gs)

layout.build()
layout.save_gds("C:/Users/nbr720/Documents/PhD/design/gds_files/Q00_20240806.gds")