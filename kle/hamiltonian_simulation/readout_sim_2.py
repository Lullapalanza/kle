import numpy as np
import matplotlib.pyplot as plt

from kle.hamiltonian_simulation.Metzger_ABS import get_coupled_Metzger_ABS

from kle.hamiltonian_simulation.ABS import (
    get_uncoupled_ABS_eigvals,
    get_coupled_ABS_hamiltonian
)

# Sss, I want to simulate the dispersive shift as a function of circuit parameters, potentially optimizing
# Maybe at some point with dissipation for limits on Qi

Q = 1.6022e-19 # 1.6022
PLANK = 6.626e-34 # 6.626e-15
HBAR = PLANK / (2 * np.pi)
EV_TO_HZ = Q / PLANK

TAU = 0.95
DELTA = 100e-6 # in eV


def get_derivative(v_m1, v_p1, delta):
    """
    Estimate derivative at index i
    """
    return (-0.5 * v_m1 + 0.5 * v_p1) / delta


if __name__ == "__main__":
    N_PHI = 401
    phis = np.linspace(2, 0, num=N_PHI) * np.pi
    delta_phi = phis[1] - phis[0]

    N_res = 2  
    L = [0, ] # [-1, 0, 1,]
    lambda_1, lambda_2 = 1, 1 # 4, 5
    
    Metzger_E = get_coupled_Metzger_ABS(TAU, lambda_1, lambda_2, phis, L)
    uncoupled_E = get_uncoupled_ABS_eigvals(lambda_1, lambda_2, phis, L)

    SOLVED_E = [
        [] for i in range(N_res * 2 * len(L))
    ]

    def general_g(epsilon_0, epsilon_1, var_tau, phi, spin_label, l_label):
        phi_i = np.where(phis == phi)[0][0]
        eps_c1 = Metzger_E[spin_label][l_label][0][phi_i]
        
        g_1 = np.sqrt(
            epsilon_1 * epsilon_0 - eps_c1 * (epsilon_0 + epsilon_1 - eps_c1), dtype=complex
        )
        
        return g_1, g_1
    
    coupled_H = get_coupled_ABS_hamiltonian(uncoupled_E, general_g, TAU, phis, total_l=len(L)*2)


    for i_phi in range(1, N_PHI-1):
        # Go through all points
        
        # In eV, need to convert to Hz
        H_ABS = EV_TO_HZ * DELTA * coupled_H[i_phi]

        dH_ABS = EV_TO_HZ * DELTA * np.diag([
            get_derivative(coupled_H[i_phi-1][j][j], coupled_H[i_phi+1][j][j], delta_phi) for j in range(len(H_ABS))
        ])

        
        r = 0.25
        Z_res = 90

        phi_brim = r * np.sqrt(HBAR * Z_res / 2)
        phi_brim_fixed = phi_brim * EV_TO_HZ

        if i_phi == 70:
            print(H_ABS)
            print(dH_ABS)
            print(phi_brim_fixed)
        # Now I have all the parts needed
        N_ABS = len(H_ABS)

        f_res = 20e9 # in Hz
        H_res = f_res * np.diag([i+1 for i in range(N_res)])

        a_res = np.diag(np.sqrt([i+1 for i in range(N_res-1)]), k=-1)
        a_dagger_res = np.diag(np.sqrt([i+1 for i in range(N_res-1)]), k=1)

        H_tot = np.kron(H_res, np.eye(N_ABS)) + np.kron(np.eye(N_res), H_ABS) + 100 * np.kron(phi_brim_fixed * (a_dagger_res + a_res), dH_ABS)

        if i_phi == 70:
            print(np.kron(H_res, np.eye(N_ABS)))
            print(np.kron(np.eye(N_res), H_ABS))
            print(np.kron(phi_brim_fixed * (a_dagger_res + a_res), dH_ABS))

        eigvals, eigvecs = np.linalg.eig(H_tot)
        sorted_eigvals = np.sort(eigvals)

        for i in range(N_res * 2 * len(L)):
            SOLVED_E[i].append(sorted_eigvals[i] - sorted_eigvals[0])



    for i, e in enumerate(SOLVED_E):
        plt.plot(phis[1:-1], e, ls="--")

    plt.plot(phis[1:-1], np.array(SOLVED_E[3]) - np.array(SOLVED_E[1]), color="gray", alpha=0.5)
    plt.show()