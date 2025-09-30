from kle.layout.layout import KleLayoutElement, create_shape, KleCutOut
from kle.layout.layout_trace_routing import get_smoothed_path, get_routed_cpw, get_routed_trace
from dataclasses import dataclass

import numpy as np

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
    
    side_gap = create_shape(layer, [
        (0, -port_width/2 - port_gap), (-port_gap, -port_width/2 - port_gap), (-port_gap, port_width/2 + port_gap), (0, port_width/2 + port_gap)
    ]).move(-taper_length - port_length, 0)
    port.add_element(side_gap)

    return port



def get_C(eps, l, N):
    return (eps + 1) * ((N-3) * 4.409e-6 + 9.92e-6) * l * 1e-12

def get_L(sheet_L, l, width):
    return sheet_L * l / width

def get_f(C, L):
    return 1 / (3.14 * 2 * (C * L)**0.5)

def get_Z(C, L):
    return (L/C)**0.5

def get_resonator_LC(f, Z0):
    C = 1/(2 * np.pi * f * Z0)
    L = C * Z0**2

    return L, C

def get_L_length(f, Z0, width=2, L_sheet=10e-12, N=5, eps=11.7):
    C = 1/(2 * 3.14 * f * Z0)
    L = C * Z0**2
    print("L:", L, "C:", C)

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
    # cutout = KleCutOut(create_shape(layer, [
    #     [0, 0],
    #     [params.cutout_width, 0],
    #     [params.cutout_width, params.cutout_height],
    #     [0, params.cutout_height]
    # ]))

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
    
    y_start = (params.meander_height - L - Wm)/2
    y_stop = (params.meander_height + L + Wm + G * 2)/2
    turn_height = (y_stop-y_start) / (params.meander_N + 1)
    
    def get_path(tlen, theight):
        path = [
            [0, y_start],
            [-10, y_start],
            [-params.meander_offset - tlen, y_start],
            [-params.meander_offset - tlen, y_start + theight]
        ]
        i = 0
        for i in range(params.meander_N):
            if i%2 == 0:
                path.extend([
                    [-params.meander_offset, y_start + theight * (i+1)],
                    [-params.meander_offset, y_start + theight * (i+2)]
                ])
            else:
                path.extend([
                    [-params.meander_offset - tlen, y_start + theight * (i+1)],
                    [-params.meander_offset - tlen, y_start + theight * (i+2)]
                ])

        path.extend([
            [-10, y_stop],
            [-1, y_stop],
            [0, y_stop]
        ])

        return path
    
    path = get_path(turn_len, turn_height)

    path, smoothed_len = get_smoothed_path(path, radii=3, phi_step=0.5)

    len_change = (params.meander_L - smoothed_len) / (params.meander_N + 2)
    turn_len += len_change
    
    path = get_path(turn_len, turn_height)
    
    trace, tr_len = get_routed_trace(layer, path, width_start=Wm, width_end=Wm, radii=3)
    
    print("tr, len:", tr_len)

    trace.add_element(interdigit_cap)
    trace.move(200, 100)
    return trace

    # cutout.add_element(trace)

    # return cutout, trace


import scipy.special as sp
import numpy as np
eps_0 = 8.8542e-12

def get_cpw_impedance(center_width, gap, L_sheet, eps, l=100, lambda_frac=0.5):
    k = center_width / (center_width + 2 * gap)
    kbrim = (1-k**2)**0.5
    mu_0 = np.pi * 4e-7

    K = sp.ellipk(k)
    Kbrim = sp.ellipk(kbrim)

    cap_per_len = 2 * eps_0 * (1+eps) * K/Kbrim
    ind_per_len = 0.25 * mu_0 * Kbrim/K

    center_width = center_width * 1e-6

    ll = ind_per_len + L_sheet/center_width
    cl = cap_per_len
    imp = (ll/cl)**0.5
    freq = 1e9/(ll*1e9 * cl*1e9)**0.5 * (1/(1e-6 * l)) 
    
    return imp, freq * lambda_frac

def get_cpw_LC(center_width, gap, L_sheet, eps, l=100):
    k = center_width / (center_width + 2 * gap)
    kbrim = (1-k**2)**0.5
    mu_0 = np.pi * 4e-7

    K = sp.ellipk(k)
    Kbrim = sp.ellipk(kbrim)

    cap_per_len = 2 * eps_0 * (1+eps) * K/Kbrim
    ind_per_len = 0.25 * mu_0 * Kbrim/K

    center_width = center_width * 1e-6

    ll = ind_per_len + L_sheet/center_width
    cl = cap_per_len

    return ll * l * 1e-6, cl *l * 1e-6


def get_coplanar_C(w, gap, eps=11.7):
    k = gap / (gap + 2 * w)
    k_brim = (1 - k**2)**0.5

    eps_r = (eps + 1) / 2 # ish 
    c = 2.998e8

    if k <= 1/(2**0.5):
        C = eps_r * np.log(2 * (1 + k_brim**0.5)/(1-k_brim**0.5))/(377 * np.pi * c)
    else:
        C = eps_r / (120 * c * np.log(2 * (1 + k**0.5)/(1-k**0.5)))

    return C


def C_air_asymmetric_stripline(w1, w2, s):
    '''
    Returns the capacitance through air of the Schuster resonator to the feedline.
    '''
    k0 = np.sqrt(s*(w1+w2+s)/((s+w1)*(s+w2)))
    k0_prime = np.sqrt(1-k0**2)
    K0 = sp.ellipk(k0)
    K0_prime = sp.ellipk(k0_prime)
    C_air = 2*eps_0*(K0_prime/K0)#**(-1)
    return C_air



def fun_k_asymmetric_stripline(w1, w2, s, h):
    '''
    Computes the argument of the elliptic integrals for the an asymmetric coplanar stripline
    This is used to compute Cc in the Schuster resonator.
    '''
    num = np.float64((np.exp(2*np.pi*(w1+s)/h) -np.exp(2*np.pi*w1/h)) * (np.exp(2*np.pi*(w1+w2+s)/h) -1))
    den = np.float64(np.exp(2*np.pi*(w1+w2+s)/h) -np.exp(2*np.pi*w1/h)) * (np.exp(2*np.pi*(w1+s)/h) -1)
    return np.sqrt(num/den)


def cap_coupling(w1, w2, gap, l, eps=11.7):
    C_air =  C_air_asymmetric_stripline(w1, w2, gap)
    k = fun_k_asymmetric_stripline(w1, w2, gap, 575)
    k_prime = (1-k**2)**0.5
    K = sp.ellipk(k)
    K_prime = sp.ellipk(k_prime)

    cap = eps_0 * eps * K_prime/K

    return (cap + C_air) * l * 1e-6