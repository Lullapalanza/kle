"""
Make copy of KR and new 2 resonator design for Lazar's chip
"""
from kle.layout.layout import KleLayout, KleLayoutElement, create_shape
from kle.layout.layout_trace_routing import (
    get_routed_cpw
)
from kle.layout.resonator_elements import get_cpw_port


layout = KleLayout(2200, 2200, ["border", "-sc", "grid"])
layers = layout.get_layers()

# ==== MAKE PL AND PORTS ====
PL_WIDTH = 14.484
PL_GAP = 8.5

pl = get_routed_cpw(
    layers["sc"],
    [(0, 0),
    (0, -100), (0, -300),
    (1000, -300), (1500, -300),
    (1500, -100), (1500, 0)],
    PL_WIDTH,
    PL_GAP,
    radii=90
)



port = get_cpw_port(
    layers["sc"],
    PL_WIDTH, PL_GAP,
    port_gap=147,
    port_width=250,
    port_length=247,
    taper_length=123,
)
port.add_element(
    create_shape(layers["sc"], [
        (-370, 125+147),
        (-370-147, 125+147),
        (-370-147, -125-145),
        (-370, -125-147)
    ])
)
port.rotate_by_angle(90)

new_port = port.get_copy().move(1500, 0)

pl.add_element(port)
pl.add_element(new_port)

layout.add_element(pl.move(350, 1600))


RES_WIDTH = 10.226
RES_GAP = 6
# resonator_0 = get_routed_cpw(
#     layers["sc"],
#     [
#         (0, 0), (-400, 0),
#         (-400, -350-2.5), (380+4+12.5, -350-2.5),
#         (380+4+12.5, -550-2.5), (-400+16-12.5, -550-2.5),
#         (-400+16-12.5, -750-2.5), (380+4+12.5, -750-2.5),
#         (380+4+12.5, -950-2.5), (-400+16-12.5, -950-2.5),
#         (-400+16-12.5, -1150-2.5), (0, -1150-2.5),
#         (0, -1520+67)
#     ],
#     RES_WIDTH,
#     RES_GAP,
#     radii=90
# )
resonator_0 = get_routed_cpw(
    layers["sc"],
    [
        (0, 0), (-580, 0),
        (-580, -352.5), (100, -352.5),
        (100, -552.5), (-580, -552.5),
        (-580, -752.5), (246.5, -752.5),
        (246.5, -952.5), (-580, -952.5),
        (-580, -1152.5), (-580 + 150 + 31 + 230*2, -1152.5),
        # (0, -1520+67)
    ],
    RES_WIDTH,
    RES_GAP,
    radii=90
)
resonator_0.add_element(
    create_shape(layers["sc"], [
        (0, RES_GAP+RES_WIDTH/2), (RES_GAP, RES_GAP+RES_WIDTH/2), (RES_GAP, -RES_GAP-RES_WIDTH/2), (0, -RES_GAP-RES_WIDTH/2)
    ])
)
layout.add_element(resonator_0.move(750, 1260+13.286-20.65))

resonator_1 = get_routed_cpw(
    layers["sc"],
    [
        (0, 0), (580, 0),
        (580, -352.5), (-100, -352.5),
        (-100, -552.5), (580, -552.5),
        (580, -752.5), (-246.5, -752.5),
        (-246.5, -952.5), (580, -952.5),
        (580, -1152.5), (580 - 50 - 31 - 230*2, -1152.5),
        # (0, -1520+67)
    ],
    RES_WIDTH,
    RES_GAP,
    radii=90
)
resonator_1.add_element(
    create_shape(layers["sc"], [
        (0, RES_GAP+RES_WIDTH/2), (-RES_GAP, RES_GAP+RES_WIDTH/2), (-RES_GAP, -RES_GAP-RES_WIDTH/2), (0, -RES_GAP-RES_WIDTH/2)
    ])
)
layout.add_element(resonator_1.move(1480, 1260+13.286-20.65))




layout.build_to_file("/home/jyrgen/Documents/PhD/design_files/KRC00_20241203.dxf")