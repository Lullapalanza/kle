"""
Lumped element resonator samples for NbTiN
"""

from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape
from kle.layout.dot_elements import (
    get_Lazar_global_markers,
    get_dot_with_leads, DotWLeadsParams,
    get_andreev_dot_with_loop, ADParams,
)
from kle.layout.layout_connections import ConnectedElement


LAYER_NAMES = [
    "SC", # Inverse base layer 
]

layout = KleLayout(10000, 10000, LAYER_NAMES)
layers = layout.get_layers()


resonator = KleLayoutElement()

# CAP
interdigit_cap = KleLayoutElement()
N = 11
L = 970
W = 3
G = 3

CON_EXTRA = 5

for n in range(N):
    interdigit_cap.add_element(
        create_shape(layers["SC"], [
            [0, 0],
            [W, 0],
            [W, L],
            [0, L]
        ]).move(n * (W + G), (n%2)*G)
    )
interdigit_cap.add_element(
    create_shape(layers["SC"], [
        [-CON_EXTRA, 0],
        [-CON_EXTRA, -W],
        [(W + G) * N - G, -W],
        [(W + G) * N - G, 0]
    ])
)
interdigit_cap.add_element(
    create_shape(layers["SC"], [
        [-CON_EXTRA, 0],
        [-CON_EXTRA, -W],
        [(W + G) * N - G, -W],
        [(W + G) * N - G, 0]
    ]).move(0, L + G + W)
)




resonator.add_element(interdigit_cap)
layout.add_element(resonator)

layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/L00_20250127.gds"
)
