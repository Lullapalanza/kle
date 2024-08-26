"""
Test design TD00 - design used for testing the generation of some elements

I uess with this one I want to try and implement automatic routing for the fanout?
Maybe also bounding boxes? That way I can have margins without having to move things myself and autocentering?
"""

from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape
from kle.layout.dot_elements import (
    get_Lazar_global_markers
)


LAYER_NAMES = [
    "-CHIP",
    "MARKERS",
    "LM0",
    "LM1",
    "LM2",
    "LM3",
]

layout = KleLayout(6000, 6000, LAYER_NAMES)
layers = layout.get_layers()

layout.add_element(get_Lazar_global_markers(layers["MARKERS"]))

# ==== START BOND PADS ====
def create_bond_pads_for_quadrant(layer):
    bond_pads = KleLayoutElement("bp")

    width = 160
    height = 160
    spacing = 160 + 50

    pad = create_shape(layer, [
        (-width/2, -height/2),
        (width/2, -height/2),
        (width/2, height/2),
        (-width/2, height/2)
    ])

    for i in range(9):
        bond_pads.add_element(pad.get_copy().move(i*spacing, 0))
        bond_pads.add_element(pad.get_copy().move(i*spacing, -1680))
        
    for i in range(7):
        bond_pads.add_element(pad.get_copy().move(0, -(i+1) * spacing))
        bond_pads.add_element(pad.get_copy().move(1680, -(i+1) * spacing))
        
    bond_pads.move(-1680/2, 1680/2)

    return bond_pads
# ==== END BOND PADS ====



# ==== LOCAL MARKERS FOR 4 QUADRANTS ====
lm_l_pos = [
    ("LM0", 1775, 4175),
    ("LM1", 3925, 4175),
    ("LM2", 1775, 2025),
    ("LM3", 3925, 2025),
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
    
    layout.add_element(create_bond_pads_for_quadrant(layers["MARKERS"]).move(x+150, y-150))
# ==== END LOCAL MARKERS ====

layout.build_to_file("C:/Users/nbr720/Documents/PhD/design/design_files/TD00_20240826.dxf")