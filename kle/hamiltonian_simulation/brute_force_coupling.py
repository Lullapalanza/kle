import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt

from kle.Metzger_ABS import get_coupled_Metzger_ABS
from kle.ABS import get_uncoupled_ABS_eigvals, get_coupled_ABS_eigvals


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



# Some brute force
def brute_force():
    phis = np.linspace(0.3, 1.7, num=101) * np.pi
    TAU = 0.9
    L = [0, ]
    u_res = get_uncoupled_ABS_eigvals(0.2, 0.05, phis, L)

    def solve_for_model(model_params):
        """
        [A, B, p]
        """
        A, B, p = model_params
        def model_callable(epsilon_0, epsilon_1, var_tau, phi):
            g = A / (np.power(B, 2) + np.power(epsilon_0 - epsilon_1, 2))
            return g, g

        res = get_coupled_ABS_eigvals(u_res, model_callable, TAU, phis, total_l=len(L)*2)
        res_M = get_coupled_Metzger_ABS(TAU, 0.2, 0.05, phis)
        m_diff = model_difference(res, res_M, spin_labels=[1])
        print(m_diff)
        return m_diff

    opt_res = opt.minimize(solve_for_model, [1.148e+00, 1.900e+00, 8.081e-01], options={"maxiter": 10})
    print(opt_res)
    
    def model_callable(epsilon_0, epsilon_1, var_tau, phi):
        A, B, p = opt_res.x
        g = A / (np.power(B, 2) + np.power(epsilon_0 - epsilon_1, 2))
        return g, g
    coupled_res = get_coupled_ABS_eigvals(u_res, model_callable, TAU, phis, total_l=len(L)*2)
    res_M = get_coupled_Metzger_ABS(TAU, 0.2, 0.05, phis)
    
    plot_for_res(phis, coupled_res, res_M)



if __name__ == "__main__":
    phis = np.linspace(2, 0, num=201) * np.pi
    TAU = 0.95
    L = [-1, 0, 1,]

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