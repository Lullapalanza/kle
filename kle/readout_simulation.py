import numpy as np
import matplotlib.pyplot as plt

from kle.andreev_bound_states import get_eigenenergies_of_ABS, PHI, N_PHI

# Sss, I want to simulate the dispersive shift as a function of circuit parameters, potentially optimizing
# Maybe at some point with dissipation for limits on Qi

ENERGIES_D, ENERGIES_U = get_eigenenergies_of_ABS()

delta_phi = PHI[1] - PHI[0]
def get_derivative(arr, i, j):
    return (-0.5 * arr[i][j-1] + 0.5 * arr[i][j+1]) / delta_phi


N_ABS = 4
N_res = 4

_TRANSITIONS = [
    [] for i in range(N_ABS * N_res - 1)
]

for i_phi in range(1, N_PHI-1):
    # Make a hamiltonian per phase point
    # Limit to only the lowest level
    # H_ABS = np.diag([
    #     ENERGIES_D[0][i_phi], ENERGIES_D[1][i_phi], ENERGIES_D[2][i_phi], ENERGIES_D[3][i_phi],
    #     ENERGIES_U[0][i_phi], ENERGIES_U[1][i_phi], ENERGIES_U[2][i_phi], ENERGIES_U[3][i_phi]
    # ])
    H_ABS = np.diag([
        ENERGIES_D[0][i_phi], ENERGIES_D[2][i_phi],
        ENERGIES_U[0][i_phi], ENERGIES_U[2][i_phi]
    ])

    dH_ABS = np.diag([
        get_derivative(ENERGIES_D, 0, i_phi),
        # get_derivative(ENERGIES_D, 1, i_phi),
        get_derivative(ENERGIES_D, 2, i_phi),
        # get_derivative(ENERGIES_D, 3, i_phi),
        get_derivative(ENERGIES_U, 0, i_phi),
        # get_derivative(ENERGIES_U, 1, i_phi),
        get_derivative(ENERGIES_U, 2, i_phi),
        # get_derivative(ENERGIES_U, 3, i_phi),    
    ])

    DELTA = 60e-6
    E = 1.60218e-19
    PLANK = 6.62607e-34
    HBAR = PLANK / (2 * np.pi)

    Z_res = 90
    p = 1 # 0.05
    phi_brim = p * 2 * np.pi * E * np.sqrt(Z_res / (np.pi * PLANK))# np.sqrt(HBAR * Z_res / 2)
    print(phi_brim)

    # Going to units of J
    H_ABS = H_ABS * DELTA * E
    dH_ABS = dH_ABS * DELTA * E

    f_res = 7e9 # in Hz
    H_res = PLANK * f_res * np.diag([i+1 for i in range(N_res)])

    a_res = np.diag(np.sqrt([i+1 for i in range(N_res-1)]), k=-1)
    a_dagger_res = np.diag(np.sqrt([i+1 for i in range(N_res-1)]), k=1)

    H_tot = np.kron(H_res, np.eye(N_ABS)) + np.kron(np.eye(N_res), H_ABS) + np.kron(phi_brim * (a_dagger_res + a_res), dH_ABS)

    eigvals, eigvecs = np.linalg.eig(H_tot)
    sorted_eigvals = np.sort(eigvals)
    transitions = (sorted_eigvals - sorted_eigvals[0])[1:] / PLANK

    for i in range(N_ABS * N_res - 1):
        _TRANSITIONS[i].append(transitions[i])

ge = np.array(_TRANSITIONS[0])
res = np.array(_TRANSITIONS[1])
ro_shift = np.array(_TRANSITIONS[2]) - ge - res

plt.axhline(2 * DELTA * E / PLANK, ls="--", color="gray")
print(ro_shift)
for i, e in enumerate(_TRANSITIONS):
    if i == 0:
        plt.plot(PHI[1:-1], np.array(e) + f_res)
    else:
        plt.plot(PHI[1:-1], e)

# plt.plot(PHI[1:-1], disp_shift)
plt.show()