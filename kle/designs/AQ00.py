"""
Ansys test file
"""
from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape
from kle.layout.dot_elements import (
    get_circle_points,
    get_dot_with_leads,
    get_andreev_dot_with_loop
)


LA_LAYERS = ["M", "G0", "G1", "O"] # Local alignment layers, gate, ohmics
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

for lid in [0, 1, 2, 3]:
    LAYER_NAMES.extend(get_layers_for_la(lid))

layout = KleLayout(6000, 6000, LAYER_NAMES)
layers = layout.get_layers()

# ==== GLOBAL MARKERS ====
marker_quadrant = KleLayoutElement("marker quadrant")
g_marker = KleLayoutElement("Global marker")

m_largearm_shape = create_shape(
    layers["MARKERS"],
    [(0, -2.5), (84, -2.5), (84, 2.5), (0, 2.5)],
)
g_marker.add_element(m_largearm_shape.get_copy())
g_marker.add_element(m_largearm_shape.get_copy().move(84 + 12, 0))
g_marker.add_element(m_largearm_shape.get_copy().rotate_left().move(84 + 6, 6))
g_marker.add_element(m_largearm_shape.get_copy().rotate_left().move(84 + 6, -84 - 6))

m_smallarm_shape = create_shape(layers["MARKERS"], [(-5, -0.25), (5, -0.25), (5, 0.25), (-5, 0.25)])
g_marker.add_element(m_smallarm_shape.get_copy().move(90, 0))
g_marker.add_element(m_smallarm_shape.get_copy().rotate_left().move(90, 0))


for i in range(5):
    marker_quadrant.add_element(g_marker.get_copy().move(200 * i, 0))

for i in range(1, 5):
    marker_quadrant.add_element(g_marker.get_copy().move(0, 200 * i))

marker_quadrant.update_origin((90, 0)).move(-90, 0)

mk_NW = marker_quadrant.get_copy().rotate_right().move(600, 5400)
mk_NE = marker_quadrant.get_copy().rotate_right().rotate_right().move(5400, 5400)
mk_SE = marker_quadrant.get_copy().rotate_left().move(5400, 600)
mk_SW = marker_quadrant.move(600, 600)

layout.add_element(mk_NW)
layout.add_element(mk_NE)
layout.add_element(mk_SE)
layout.add_element(mk_SW)
# ==== END GLOBAL MARKERS ====


# ==== LOCAL MARKERS FOR 4 QUADRANTS ====
lm_l_pos = [
    ("M_0", 1775, 4175),
    ("M_1", 3925, 4175),
    ("M_2", 1775, 2025),
    ("M_3", 3925, 2025),
]

for l, x, y in lm_l_pos:
    lm = KleLayoutElement(f"Local markers {l}")
    lms = create_shape(
        layers[l], [
            (-11, -1.25), (-1.25, -1.25), (-1.25, -11), (1.25, -11), (1.25, -1.25),
            (11, -1.25), (11, 1.25), (1.25, 1.25), (1.25, 11), (-1.25, 11),
            (-1.25, 1.25), (-11, 1.25)
        ]
    )
    positions = [
        (0, 0), (20, -20), (40, -40),
        (300, 0), (280, -20), (260, -40),
        (0, -300), (20, -280), (40, -260),
        (300, -300), (280, -280), (260, -260)
    ]
    for p in positions:
        lm.add_element(lms.get_copy().move(*p))
    layout.add_element(lm.move(x, y))
# ==== END LOCAL MARKERS ====



# The device is split into 4
# 1st and second are double devices with different dot size with and without loop

# ==== AQD (loop) + AQD (loop) / AQD (leads) + AQD (leads) ====
# 220 * 220 local alignemnt square where to draw

# First the DOTS
first_quadrant = KleLayoutElement("first quadrant")

CS_AQ_0 = KleLayoutElement("CS, AQ")
CD_R = 0.175/2
CS_AQ_0.add_element(get_dot_with_leads(
    layers["O_0"],
    layers["G0_0"],
    layers["G1_0"],
    dot_r=CD_R
))
AD_R = 0.2/2
CS_AQ_0.add_element(get_andreev_dot_with_loop(
    layers["O_0"],
    layers["G0_0"],
    layers["G1_0"],
    dot_r=AD_R
).move(CD_R + AD_R + 0.055, 0))
barrier = create_shape(layers["G1_0"], [(0, -0.060), (0.04, -0.060), (0.04, 0.060), (0, 0.060)])
CS_AQ_0.add_element(barrier.get_copy().move(CD_R + 0.0075, 0))
first_quadrant.add_element(CS_AQ_0)

# CSAQ1
CS_AQ_1 = KleLayoutElement("CS, AQ")
CD_R = 0.175/2
CS_AQ_1.add_element(get_dot_with_leads(
    layers["O_0"],
    layers["G0_0"],
    layers["G1_0"],
    dot_r=CD_R
))
AD_R = 0.25/2
CS_AQ_1.add_element(get_andreev_dot_with_loop(
    layers["O_0"],
    layers["G0_0"],
    layers["G1_0"],
    dot_r=AD_R
).move(CD_R + AD_R + 0.055, 0))
barrier = create_shape(layers["G1_0"], [(0, -0.060), (0.04, -0.060), (0.04, 0.060), (0, 0.060)])
CS_AQ_1.add_element(barrier.get_copy().move(CD_R + 0.0075, 0))
first_quadrant.add_element(CS_AQ_1.move(3.1 + 0.025, 0).flip_horizontally())

# Update center
first_quadrant.update_origin((1.55, 0))
first_quadrant.move(-1.55, 0)

# Add stripline
SL_HEIGHT = 50
SL_WIDTH = 0.5
stripline = create_shape(layers["O_0"], [
    (-SL_WIDTH/2, -SL_HEIGHT/2),
    (SL_WIDTH/2, -SL_HEIGHT/2),
    (SL_WIDTH/2, SL_HEIGHT/2),
    (-SL_WIDTH/2, SL_HEIGHT/2),
])
first_quadrant.add_element(stripline)

first_quadrant.move(1775 + 150, 4175 - 150)

layout.add_element(first_quadrant)
# ===== END AQD + CS ====






# Second quadrant with leaded AQ + CS
second_quadrant = KleLayoutElement("second quadrant")

CS_AQ_0 = KleLayoutElement("CS, AQ")
CD_R = 0.175/2
CS_AQ_0.add_element(get_dot_with_leads(
    layers["O_1"],
    layers["G0_1"],
    layers["G1_1"],
    dot_r=CD_R
))
AD_R = 0.2/2
CS_AQ_0.add_element(get_dot_with_leads(
    layers["O_1"],
    layers["G0_1"],
    layers["G1_1"],
    dot_r=AD_R
).move(CD_R + AD_R + 0.055, 0))
barrier = create_shape(layers["G1_1"], [(0, -0.060), (0.04, -0.060), (0.04, 0.060), (0, 0.060)])
CS_AQ_0.add_element(barrier.get_copy().move(CD_R + 0.0075, 0))
second_quadrant.add_element(CS_AQ_0)

# CSAQ1
CS_AQ_1 = KleLayoutElement("CS, AQ")
CD_R = 0.175/2
CS_AQ_1.add_element(get_dot_with_leads(
    layers["O_1"],
    layers["G0_1"],
    layers["G1_1"],
    dot_r=CD_R
))
AD_R = 0.25/2
CS_AQ_1.add_element(get_dot_with_leads(
    layers["O_1"],
    layers["G0_1"],
    layers["G1_1"],
    dot_r=AD_R
).move(CD_R + AD_R + 0.055, 0))
barrier = create_shape(layers["G1_1"], [(0, -0.060), (0.04, -0.060), (0.04, 0.060), (0, 0.060)])
CS_AQ_1.add_element(barrier.get_copy().move(CD_R + 0.0075, 0))
second_quadrant.add_element(CS_AQ_1.move(1.4 + 0.025, 0).flip_horizontally())

# Update center
second_quadrant.update_origin((0.7, 0))
second_quadrant.move(-0.7, 0)
second_quadrant.move(3925 + 150, 4175 - 150)
layout.add_element(second_quadrant)






# 3rd and fourth quadrant are double dot designs with a loop
# Double CS + dot + AQloop

def get_dad(ohm_layer, gate_0_layer, gate_1_layer, position):
    quadrant = KleLayoutElement("quadrant")
    CS_AQ_0 = KleLayoutElement("CS, AQ")
    CD_R = 0.175/2
    CS_AQ_0.add_element(get_dot_with_leads(
        ohm_layer,
        gate_0_layer,
        gate_1_layer,
        dot_r=CD_R
    ))
    DOT_R = 0.100/2
    CS_AQ_0.add_element(create_shape(gate_0_layer, get_circle_points(DOT_R)).move(CD_R + DOT_R + 0.055, 0))
    barrier = create_shape(gate_1_layer, [(0, -0.060), (0.04, -0.060), (0.04, 0.060), (0, 0.060)])
    CS_AQ_0.add_element(barrier.get_copy().move(CD_R + 0.0075, 0))

    AD_R = 0.2/2
    CS_AQ_0.add_element(get_andreev_dot_with_loop(
        ohm_layer,
        gate_0_layer,
        gate_1_layer,
        dot_r=AD_R
    ).move(CD_R + DOT_R * 2 + AD_R + 0.055 * 2, 0))
    CS_AQ_0.add_element(barrier.get_copy().move(CD_R + 0.0075 + 0.055 + DOT_R * 2, 0))
    quadrant.add_element(CS_AQ_0)

    # CSAQ1
    CS_AQ_1 = KleLayoutElement("CS, AQ")
    CD_R = 0.175/2
    CS_AQ_1.add_element(get_dot_with_leads(
        ohm_layer,
        gate_0_layer,
        gate_1_layer,
        dot_r=CD_R
    ))
    DOT_R = 0.100/2
    CS_AQ_1.add_element(create_shape(gate_0_layer, get_circle_points(DOT_R)).move(CD_R + DOT_R + 0.055, 0))
    barrier = create_shape(gate_1_layer, [(0, -0.060), (0.04, -0.060), (0.04, 0.060), (0, 0.060)])
    CS_AQ_1.add_element(barrier.get_copy().move(CD_R + 0.0075, 0))

    AD_R = 0.25/2
    CS_AQ_1.add_element(get_andreev_dot_with_loop(
        ohm_layer,
        gate_0_layer,
        gate_1_layer,
        dot_r=AD_R
    ).move(CD_R + DOT_R * 2 + AD_R + 0.055 * 2, 0))
    CS_AQ_1.add_element(barrier.get_copy().move(CD_R + 0.0075 + 0.055 + DOT_R * 2, 0))

    quadrant.add_element(CS_AQ_1.move(3.4 + 0.025, 0).flip_horizontally())

    # Update center
    quadrant.update_origin((1.7, 0))
    quadrant.move(-1.7, 0)

    # Add stripline
    SL_HEIGHT = 50
    SL_WIDTH = 0.5
    stripline = create_shape(ohm_layer, [
        (-SL_WIDTH/2, -SL_HEIGHT/2),
        (SL_WIDTH/2, -SL_HEIGHT/2),
        (SL_WIDTH/2, SL_HEIGHT/2),
        (-SL_WIDTH/2, SL_HEIGHT/2),
    ])
    quadrant.add_element(stripline)
    quadrant.move(position[0] + 150, position[1] - 150)
    return quadrant

layout.add_element(
    get_dad(layers["O_2"], layers["G0_2"], layers["G1_2"], (1775, 2025))
)
layout.add_element(
    get_dad(layers["O_3"], layers["G0_3"], layers["G1_3"], (3925, 2025))
)

layout.build()
layout.save_gds("C:/Users/jyrgen/Documents/PhD/design/gds_files/AQ00_20240815.dxf")