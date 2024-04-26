import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt

from kle.hamiltonian_simulation.Metzger_ABS import get_coupled_Metzger_ABS
from kle.hamiltonian_simulation.ABS import get_uncoupled_ABS_eigvals, get_coupled_ABS_eigvals


def test_callable(epsilon_0, epsilon_1, var_tau, phi):
    T0 = 1 / (
        (1-epsilon_0**2) * (2/var_tau - 1)**2 + epsilon_0**2
    )
    T1 = 1 / (
        (1-epsilon_1**2) * (2/var_tau - 1)**2 + epsilon_1**2
    )
    R0 = 1 - T0
    R1 = 1 - T1
    return R0, R1


def model_difference(results_1, results_2, spin_labels):
    tot_error = 0
    for spin in spin_labels:
        for i in range(2):
            tot_error += np.sum(np.power(np.abs(results_1[spin][i] - results_2[spin][i]), 2))
    return np.sqrt(tot_error)


def plot_for_res(phis, res1, res2):
    for spin, (data, data_M) in enumerate(zip(res1.values(), res2.values())):
        if spin == 0:
            color = "blue"
            color_m = "teal"
        else:
            color = "red"
            color_m = "orange"
        
        for d in data:
            plt.plot(phis, d, color=color)

        for l_data in data_M.values():
            for e_p in l_data:
                plt.plot(phis, e_p, color=color_m, ls="--", alpha=0.7)



if __name__ == "__main__":
    phis = np.linspace(2, 0, num=201) * np.pi
    TAU = 0.95
    L = [0, ]# [-1, 0, 1,]

    lambda_1, lambda_2 = 4, 5
    res_M = get_coupled_Metzger_ABS(TAU, lambda_1, lambda_2, phis, L)
    
    u_res = get_uncoupled_ABS_eigvals(lambda_1, lambda_2, phis, L)
    for spin, data in u_res.items():
        for l_label, l_data in data.items():
            plt.plot(phis, l_data[0], ls="--", alpha=0.5, color="gray")
            plt.plot(phis, l_data[1], ls="--", alpha=0.5, color="gray")

    def short_g(epsilon_0, epsilon_1, var_tau, phi):
        g = np.sqrt(
            epsilon_1 * epsilon_0 + 0.5 * var_tau * (np.cos(phi) - 1) + 1
        )
        return g, g

    def long_g(epsilon_0, epsilon_1, var_tau, phi):
        g = np.sqrt(
            epsilon_1 * epsilon_0 + (1 / (lambda_1 + lambda_2)**2) * np.arccos(
                -np.cos(phi)/(2/var_tau - 1)
            )**2
        )
        return g, g

    def extended_long_g(epsilon_0, epsilon_1, var_tau, phi, spin_label, l_label):
        phi_i = np.where(phis == phi)[0][0]
        eps_c1 = res_M[spin_label][l_label][0][phi_i]
        
        g_1 = np.sqrt(
            epsilon_1 * epsilon_0 - eps_c1 * (epsilon_0 + epsilon_1 - eps_c1), dtype=complex
        )
        
        return g_1, g_1

    res = get_coupled_ABS_eigvals(u_res, extended_long_g, TAU, phis, total_l=len(L)*2)
    
    plot_for_res(phis, res, res_M)

    plt.ylabel(r"$\epsilon / \Delta$")
    plt.xlabel(r"$\phi$")
    plt.legend(
        bbox_to_anchor=(1, 1),
        title=r"$\tau =" + f"{TAU}" + r"$" + "\n" + r"$\lambda_1=" + f"{lambda_1}" + r"$" + "\n" + r"$\lambda_2=" + f"{lambda_2}" + r"$" 
    )

    plt.axhline(-1, ls="--", color="gray")
    plt.axhline(1, ls="--", color="gray")

    # plt.xlim(0, 2 * np.pi)
    plt.ylim(-1, 1)
    plt.xlim(0, 2 * np.pi)
    plt.tight_layout()

    plt.show()
    plt.close()