"""
This is the first design for a resonator test, both for fab training and maybe CD

A reflection slot line resonator PL with N resonators
"""
from kle.layout.layout import Layout
from kle.layout.layout_element import LayoutElement, Polygon
from kle.layout.layout_defaults import (
    get_rf_slot_port,
    get_chip_edges,
    get_simple_interdigit_cap
)


layout = Layout("D000", ["border", "sc"])
layers = layout.get_layers()

# Add chip border
edges = get_chip_edges(layers["border"])
layout.add_element(edges)


# Add probe line
PL_WIDTH = 10
PL_LENGTH = 2500
PL_GAP = 3

pl_0 = LayoutElement("probe_line_0")
port1 = get_rf_slot_port(layers["sc"], transmission_line_width=PL_WIDTH)
port2 = port1.get_copy().rotate_left().rotate_left().move(PL_LENGTH+400, 100 + PL_WIDTH + PL_GAP)
pl_0.add_elements([
    port1, port2
])

pl_strip = Polygon(
    layers["sc"],
    [
        (200, 50-PL_WIDTH/2),
        (200+PL_LENGTH, 50-PL_WIDTH/2),
        (200+PL_LENGTH, 50+PL_WIDTH/2),
        (200, 50+PL_WIDTH/2)
    ]
)
pl_0.add_elements([
    pl_strip, pl_strip.get_copy().move(0, PL_WIDTH + PL_GAP)
])


# resonator_positions = [
#     400 + 300 * i for i in range(int(2400/300))
# ]
# res_lengths = [
#     1200 + 100 * i for i in range(int(2400/300)) 
# ]
resonator_positions = [
    1500
]
res_lengths = [
    1200
]

for pos, res_len in zip(resonator_positions, res_lengths):
    res = LayoutElement("resonator")
    res.add_element(get_simple_interdigit_cap(layers["sc"]))
    res.add_element(
        Polygon(
            layers["sc"],
            [
                (0, 0), (0, -res_len), (PL_WIDTH + PL_GAP, -res_len),
                (PL_WIDTH + PL_GAP, -res_len + PL_GAP),
                (PL_WIDTH + PL_GAP, -res_len + PL_GAP),
                (PL_WIDTH, -res_len + PL_GAP),
                (PL_WIDTH, 0)
            ]
        ).move(15, -3)
    )
    res.add_element(
        Polygon(
            layers["sc"],
            [
                (0, 0), (0, -2500), (PL_WIDTH, -2500), (PL_WIDTH, 0)
            ]
        ).move(PL_WIDTH + PL_GAP + 15, -27)
    )
    pl_0.add_element(
        res.move(pos, 27)
    )


pl_0.move(50, 2500) # Move port to top left
pl_0.add_element(
    Polygon(
        layers["sc"],
        [
            (300, 0),
            (300, 100),
            (2700, 100),
            (2700, 0),
        ]
    )
)
layout.add_element(pl_0)

layout.build()
layout.save_gds("C:/Users/jyrgen/Documents/PhD/design/gds_files/D000.gds")