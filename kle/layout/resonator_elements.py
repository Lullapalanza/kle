from kle.layout.layout import KleLayoutElement, create_shape, KleCutOut
from kle.layout.layout_trace_routing import get_smoothed_path, get_routed_cpw, get_routed_trace
from dataclasses import dataclass


def get_cpw_port(layer, connection_width, connection_gap, port_gap=10, port_width=80, port_length=80, taper_length=80):
    port = KleLayoutElement()

    top_gap = create_shape(layer, [
        (0, connection_width/2),
        (0, connection_width/2 + connection_gap),
        (-taper_length, port_width/2 + port_gap),
        (-taper_length -port_length, port_width/2 + port_gap),
        (-taper_length -port_length, port_width/2),
        (-taper_length, port_width/2)
        
    ])
    port.add_element(top_gap.get_copy())
    port.add_element(top_gap.get_copy().flip_vertically())
    
    return port



def get_C(eps, l, N):
    return (eps + 1) * ((N-3) * 4.409e-6 + 9.92e-6) * l * 1e-12

def get_L(sheet_L, l, width):
    return sheet_L * l / width

def get_f(C, L):
    return 1 / (3.14 * 2 * (C * L)**0.5)

def get_Z(C, L):
    return (L/C)**0.5

def get_L_length(f, Z0, width=2, L_sheet=10e-12, N=5, eps=11.7):
    C = 1/(2 * 3.14 * f * Z0)
    L = C * Z0**2
    print("L:", L)

    meander_len = L * width / L_sheet
    cap_len = C / ((eps + 1) * ((N-3) * 4.409e-18 + 9.92e-18))

    return meander_len, cap_len
    

@dataclass
class LCParams:
    cutout_width: float = 300.0
    cutout_height: float = 300.0

    interdigit_cap_N: int = 5
    interdigit_cap_L: float = 60.0
    interdigit_cap_W: float = 2.0
    interdigit_cap_G: float = 2.0

    meander_W: float = 2.0
    meander_L: float = 600
    meander_height: float = 100.0
    meander_N: int = 2
    meander_offset: float = 50.0


def get_interdigit_LC(layer, params=LCParams()):
    cutout = KleCutOut(create_shape(layer, [
        [0, 0],
        [params.cutout_width, 0],
        [params.cutout_width, params.cutout_height],
        [0, params.cutout_height]
    ]))

    # Interdigit Cap
    W, L, G, N = params.interdigit_cap_W, params.interdigit_cap_L, params.interdigit_cap_G, params.interdigit_cap_N
    interdigit_cap = KleLayoutElement()
    for n in range(N):
        interdigit_cap.add_element(
            create_shape(layer, [
                [0, 0],
                [W, 0],
                [W, L],
                [0, L]
            ]).move(n * (W + G), (n%2)*G)
        )
    end_conn = create_shape(layer, [
        [-0, 0],
        [-0, -W],
        [(W + G) * N - G, -W],
        [(W + G) * N - G, 0]
    ])
    interdigit_cap.add_element(end_conn)
    interdigit_cap.add_element(end_conn.get_copy().move(0, L + G + W))
    interdigit_cap.move(0, (params.meander_height - L)/2)

    # meander
    Wm = params.meander_W
    turn_len = (params.meander_L - params.meander_offset*2 - params.meander_height) / (params.meander_N + 2)
    turn_height = params.meander_height / (params.meander_N + 1)
    print(turn_height)
    
    def get_path(tlen, theight):
        path = [
            [0, -Wm/2 + (params.meander_height - L)/2],
            [-10, -Wm/2 + (params.meander_height - L)/2],
            [-10, -Wm/2],
            [-params.meander_offset - tlen, -Wm/2],
            [-params.meander_offset - tlen, -Wm/2 + theight]
        ]
        for i in range(params.meander_N):
            if i%2 == 0:
                path.extend([
                    [-params.meander_offset, -Wm/2 + theight * (i+1)],
                    [-params.meander_offset, -Wm/2 + theight * (i+2)]
                ])
            else:
                path.extend([
                    [-params.meander_offset - tlen, -Wm/2 + theight * (i+1)],
                    [-params.meander_offset - tlen, -Wm/2 + theight * (i+2)]
                ])

        path.extend([
            [-params.meander_offset - tlen, Wm/2 + params.meander_height + G],
            [-10, Wm/2 + params.meander_height + G],
            [-10, Wm/2 + params.meander_height/2 + L/2 + G],
            [-1, Wm/2 + params.meander_height/2 + L/2 + G],
            [0, Wm/2 + params.meander_height/2 + L/2 + G]
        ])
        return path
    
    path = get_path(turn_len, turn_height)

    path, smoothed_len = get_smoothed_path(path, radii=3, phi_step=0.5)

    len_change = (params.meander_L - smoothed_len) / (params.meander_N + 2)
    turn_len += len_change
    
    path = get_path(turn_len, turn_height)
    
    trace, tr_len = get_routed_trace(layer, path, width_start=W, width_end=W, radii=3)
    
    trace.add_element(interdigit_cap)
    trace.move(200, 100)

    cutout.add_element(trace)
    # cutout.add_element(trace.move(200, 100))
    # cutout.add_element(interdigit_cap.move(200, 100))
    # cutout.flip_vertically()

    return cutout, trace


import scipy.special as sp
import numpy as np
def get_impedance(center_width, gap, L_sheet, eps):
    k = center_width / (center_width + 2 * gap)
    kbrim = (1-k**2)**0.5
    eps_0 = 8.8542e-12
    mu_0 = np.pi * 4e-7

    K = sp.ellipk(k)
    Kbrim = sp.ellipk(kbrim)

    cap_per_len = 2 * eps_0 * (1+eps) * K/Kbrim
    ind_per_len = 0.25 * mu_0 * Kbrim/K

    return ((ind_per_len + L_sheet/center_width)/cap_per_len)**0.5