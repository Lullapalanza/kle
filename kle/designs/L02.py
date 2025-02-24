"""
Double pad resonators - transmon double pad designs ish

Seems to actually be tough to be
"""


from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape, KleCutOut
from kle.layout.dot_elements import (
    get_Lazar_global_markers,
    get_dot_with_leads, DotWLeadsParams,
    get_andreev_dot_with_loop, ADParams,
)
from kle.layout.resonator_elements import get_cpw_port, get_interdigit_LC, get_L_length, LCParams, get_cpw_impedance
from kle.layout.layout_trace_routing import get_routed_cpw, get_routed_trace
from kle.layout.layout_connections import ConnectedElement


LSHEET = 111e-12
EPS = 11.7


LAYER_NAMES = [
    "SC",
]

layout = KleLayout(6000, 6000, LAYER_NAMES)
layers = layout.get_layers()

# ==== Border ====
border_shape = create_shape(layers["SC"], [
    [200, 200], [5800, 200], [5800, 300], [200, 300]
])
layout.add_element(border_shape)
layout.add_element(border_shape.get_copy().move(0, 5500))
layout.add_element(border_shape.get_copy().rotate_right().move(0, 6000))
layout.add_element(border_shape.get_copy().rotate_right().move(5500, 6000))
# ==== END BORDER ====


# ===== PL ======
PL_WIDTH = 120
PL_GAP = 2
pl, pl_length = get_routed_cpw(
    layers["SC"],
    [(0, 0),
    (100, 0), (500, 0),
    (1000, 0), (1500, 0),
    (2000, 0), (2500, 0),
    (3000, 0), (3580, 0)],
    PL_WIDTH,
    PL_GAP,
    radii=40
)

PORT_GAP = 5 * PL_GAP
PORT_WIDTH = 2 * PL_WIDTH
PORT_LEN = 120

pl.add_element(
    get_cpw_port(layers["SC"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=PORT_WIDTH, port_length=PORT_LEN)
)
pl.add_element(
    get_cpw_port(layers["SC"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=PORT_WIDTH, port_length=PORT_LEN).flip_horizontally().move(3580, 0)
)
layout.add_element(pl.move(460 + 500 + 250, 3000))

port_imp, _ = get_cpw_impedance(PORT_WIDTH, PORT_GAP, L_sheet=LSHEET, eps=EPS)
print("port imp", port_imp)

pl_imp, pl_freq = get_cpw_impedance(PL_WIDTH, PL_GAP, L_sheet=LSHEET, eps=EPS, l=pl_length + 2*PORT_LEN)
print("Probe line impedance:", pl_imp, "freq:", pl_freq/1e9)
# ======= END PROBE LINE ==========



# ===== DOUBLE PAD RESONATOR ======
import numpy as np
from kle.layout.resonator_elements import get_resonator_LC, cap_coupling

f = 8e9
Z = 1e3
g = 4e6

L, C = get_resonator_LC(f, Z)

print("Meander len:", L * 2 / LSHEET)

double_cap_spacing = 2

PAD_WIDTH = 50

l0 = 200
double_cap = cap_coupling(PAD_WIDTH, PAD_WIDTH, double_cap_spacing, l0)
l = l0 * C/double_cap

double_cap = cap_coupling(PAD_WIDTH, PAD_WIDTH, double_cap_spacing, l)

print("l:", l, "C:", double_cap)

E = 1.602e-19
PLANK = 6.626e-34
def get_g(C, f0, Z0, f1, Z1):
    return 4 * E**2 * C * f0 * f1 * Z0 * Z1 * 4 * np.pi**2 / PLANK


distance = 300
pl_cap = cap_coupling(PAD_WIDTH, PL_WIDTH, distance, l)
calc_g = get_g(pl_cap, f, Z, f, pl_imp)
print("g (MHz):", calc_g/1e6, pl_cap)

def get_pads(layer, width, gap, length):
    pads = KleLayoutElement()
    pad_shape = create_shape(layer, [
        (0, 0), (length, 0), (length, width), (0, width)
    ])
    pads.add_element(pad_shape.get_copy())
    pads.add_element(pad_shape.get_copy().move(0, width + gap))

    return pads

res = get_pads(layers["SC"], PAD_WIDTH, double_cap_spacing, l)
layout.add_element(res.flip_vertically().move(3000, 2940-distance))

    
# 2940

# ===== END DOUBLE PAD RESONATOR =====

layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/L02_111pH_11_7eps_20250220.cif"
)