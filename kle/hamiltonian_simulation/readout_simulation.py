import numpy as np
import matplotlib.pyplot as plt


# Sss, I want to simulate the dispersive shift as a function of circuit parameters, potentially optimizing
# Maybe at some point with dissipation for limits on Qi


N_RES = 3
N_ABS = 1


def get_derivative(arr, i):
    return (-0.5 * arr[i-1] + 0.5 * arr[i+1]) / delta_phi



TAU = 0.95
N_ABS = 2.25
N_res = 2

DELTA = 180e-6

_TRANSITIONS = [
    [] for i in range(N_ABS * N_res)
]

for i_phi in range(1, N_PHI-1):
    # Make a hamiltonian per phase point
    # Limit to only the lowest level
    H_ABS = DELTA * np.array([
        [E011[i_phi], get_R(E011[i_phi], E0m11[i_phi], TAU), 0, 0],
        [get_R(E011[i_phi], E0m11[i_phi], TAU), E0m11[i_phi], 0, 0],
        [0, 0, E01m1[i_phi], get_R(E01m1[i_phi], E0m1m1[i_phi], TAU)],
        [0, 0, get_R(E01m1[i_phi], E0m1m1[i_phi], TAU), E0m1m1[i_phi]]
    ])

    dH_ABS = DELTA * np.diag([
        get_derivative(E011, i_phi),
        get_derivative(E0m11, i_phi),
        get_derivative(E01m1, i_phi),
        get_derivative(E0m1m1, i_phi)
    ])

    E = 1.60218e-19
    PLANK = 6.62607e-34
    HBAR = PLANK / (2 * np.pi)

    Z_res = 90
    p = 0.25
    phi_brim = p * np.sqrt(HBAR * Z_res / 2) * 2 * E / PLANK

    # print(phi_brim / PLANK)

    # Going to units of J
    H_ABS = H_ABS * E
    dH_ABS = dH_ABS * E

    f_res = 7e9 # in Hz
    H_res = PLANK * f_res * np.diag([i+1 for i in range(N_res)])

    a_res = np.diag(np.sqrt([i+1 for i in range(N_res-1)]), k=-1)
    a_dagger_res = np.diag(np.sqrt([i+1 for i in range(N_res-1)]), k=1)

    H_tot = np.kron(H_res, np.eye(N_ABS)) + np.kron(np.eye(N_res), H_ABS) + np.kron(phi_brim * (a_dagger_res + a_res), dH_ABS)

    eigvals, eigvecs = np.linalg.eig(H_tot)
    sorted_eigvals = np.sort(eigvals)
    # transitions = (sorted_eigvals - sorted_eigvals[0])[1:] / PLANK

    for i in range(N_ABS * N_res):
        _TRANSITIONS[i].append((sorted_eigvals[i] - sorted_eigvals[0]) / PLANK)

# ge = np.array(_TRANSITIONS[0])
# res = np.array(_TRANSITIONS[1])
# ro_shift = np.array(_TRANSITIONS[2]) - ge - res

# plt.axhline(2 * DELTA * E / PLANK, ls="--", color="gray")
# print(ro_shift)
for i, e in enumerate(_TRANSITIONS):
    plt.plot(PHI[1:-1], e, ls="--")

plt.plot(PHI[1:-1], np.array(_TRANSITIONS[3]) - np.array(_TRANSITIONS[1]), color="black")

# plt.plot(PHI[1:-1], disp_shift)
plt.show()