"""
EBL dose test
"""
from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape, KleCutOut, create_ref
from kle.layout.dot_elements import (
    get_Lazar_global_markers,
    get_dot_with_leads, DotWLeadsParams,
    get_andreev_dot_with_loop, ADParams,
)
from kle.layout.resonator_elements import get_resonator_LC, get_coplanar_C, get_cpw_port, get_interdigit_LC, get_L_length, LCParams, get_cpw_impedance
from kle.layout.layout_trace_routing import get_routed_cpw, get_routed_trace
from kle.layout.layout_connections import ConnectedElement
from kle.layout.resonator_elements import get_cpw_LC


LSHEET = 600e-12 # 600 ph/sq
EPS = 11.7

LAYER_NAMES = [
    "SC_FINE", "SC_COARSE"
]
layout = KleLayout(10000, 10000, LAYER_NAMES)
layers = layout.get_layers()

# === TEMP ==== FOR DOSE TEST
def get_meander_path(height, step, N):
    path = [
        (-20, 0)
    ]
    for i in range(N):
        if i%2 == 0:
            path.extend([
                (height, -step * i),
                (height, -step * (i + 1))
            ])
        else:
            path.extend([
                (0, -step * i),
                (0, -step * (i + 1))
            ])

    path = path[:-1] + [(height * ((i+1)%2), -step * (i + 0.5)), (path[-1][0], path[-1][1]-20)]

    return path


# poss = [
#     (50, 300), (250, 300), (50, 140), (250, 140)
# ]
# H, S = 100, 2
# DT_cutout = KleCutOut(create_shape(layers["SC"], [
#     (0, 0), (400, 0), (400, 400), (0, 400)
# ]))
# for W, pos in zip([0.1, 0.25, 0.5, 1], poss):
# # W = 0.5
#     S = W * 2.5
#     DT_trace, _ = get_routed_trace(layers["SC"], get_meander_path(H, S, 30), width_start=W, width_end=W, radii=W*1.2)
#     DT_cutout.add_element(DT_trace.move(*pos))

trace, _ = get_routed_trace(layers["SC_FINE"], get_meander_path(40, 2, 10), width_start=0.5, width_end=0.5, radii=0.5 * 1.2)
layout.add_element(trace)

trace, _ = get_routed_trace(layers["SC_FINE"], get_meander_path(40, 1, 10), width_start=0.5, width_end=0.5, radii=0.5 * 1.1)
layout.add_element(trace.move(100, 0))

trace, _ = get_routed_trace(layers["SC_FINE"], get_meander_path(40, 0.8, 10), width_start=0.2, width_end=0.2, radii=0.2 * 1.2)
layout.add_element(trace.move(0, -50))

trace, _ = get_routed_trace(layers["SC_FINE"], get_meander_path(40, 0.4, 10), width_start=0.2, width_end=0.2, radii=0.2 * 1.1)
layout.add_element(trace.move(100, -50))


trace, _ = get_routed_trace(layers["SC_FINE"], get_meander_path(40, 0.4, 10), width_start=0.1, width_end=0.1, radii=0.1 * 1.2)
layout.add_element(trace.move(0, -100))

trace, _ = get_routed_trace(layers["SC_FINE"], get_meander_path(40, 0.2, 10), width_start=0.1, width_end=0.1, radii=0.1 * 1.1)
layout.add_element(trace.move(100, -100))


trace, _ = get_routed_trace(layers["SC_COARSE"], get_meander_path(40, 5, 10), width_start=2, width_end=2, radii=2 * 1.2)
layout.add_element(trace.move(200, -30))


layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/EDT_600ph_11_7eps_20250821.cif"
)


# print("1", get_cpw_impedance(1, 20, 0, EPS, 1500))
# print("2", get_cpw_impedance(20, 1, 0, EPS, 1500))