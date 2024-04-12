import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt


def labeled_uncoupled_ABS(epsilon, phi, l, lambda_sum, lambda_diff, p, sigma):
    return (2 * p / lambda_sum) * (
        sigma * 0.5 * epsilon * lambda_diff + phi/2 - p * np.arcsin(epsilon) + np.pi * (p * l - 0.5)
    ) - epsilon


def get_uncoupled_ABS_eigvals(lambda_1, lambda_2, list_of_phi, list_of_l):
    results = {
        -1: {
            l: [] for l in list_of_l # lR and L
        },
        1: {
            l: [] for l in list_of_l
        }
    }

    for sigma in [-1, 1]:
        for direction in [-1, 1]:
            for l in list_of_l:
                phi_results = np.empty((len(list_of_phi)))
                phi_results[:] = np.nan
                for i, p in enumerate(list_of_phi):
                    args = (p, l, lambda_1 + lambda_2, lambda_1 - lambda_2, direction, sigma)
                    e_at_p = opt.root(labeled_uncoupled_ABS, 0.1, args=args, method="hybr", options={"factor": 1})
                    if e_at_p.success:
                        phi_results[i] = e_at_p.x[0] 

                results[sigma][l].append(
                    phi_results
                )

    return results


def _get_new_arr(length):
    _new_arr = np.empty(length)
    _new_arr[:] = np.nan
    return _new_arr


def get_coupled_ABS_hamiltonian(uncoupled_res, scattering_callable, tau, list_of_phi, total_l):
    results = []

    for spin_label, spin_data in uncoupled_res.items():
        H_dim = len(spin_data) * 2

        for i_phi, phi in enumerate(list_of_phi):
            H_scattering = np.zeros((H_dim, H_dim))
            prev_E = None
            for i_l, l_data in enumerate(spin_data.values()):
                l_label = list(spin_data.keys())[i_l]
                for p in [0, 1]:
                    H_scattering[2 * i_l + p][2 * i_l + p] = l_data[p][i_phi]

                    if prev_E is not None:
                        scattering_coupling_0, scattering_coupling_1 = scattering_callable(prev_E, l_data[p][i_phi], tau, phi, spin_label, l_label)

                        H_scattering[2 * i_l + p][2 * i_l + p - 1] = scattering_coupling_0
                        H_scattering[2 * i_l + p - 1][2 * i_l + p] = scattering_coupling_1

                    if p == 1 and i_l > 0:
                        scattering_coupling_0, scattering_coupling_1 = scattering_callable(
                            H_scattering[2 * i_l + p - 3][2 * i_l + p -3], l_data[p][i_phi],
                            tau, phi, spin_label, l_label
                        )
                    
                        H_scattering[2 * i_l + p][2 * i_l + p - 3] = scattering_coupling_0
                        H_scattering[2 * i_l + p - 3][2 * i_l + p] = scattering_coupling_1

                    prev_E = l_data[p][i_phi]


            results.append(H_scattering)

    return results



def get_coupled_ABS_eigvals(uncoupled_res, scattering_callable, tau, list_of_phi, total_l):
    """
    Using uncoupled values find new eigenenergies
    """

    results = {
        -1: [_get_new_arr(len(list_of_phi)) for _ in range(total_l)],
        1: [_get_new_arr(len(list_of_phi)) for _ in range(total_l)]
    }
    # different spin labels can be done independently
    for spin_label, spin_data in uncoupled_res.items():
        H_dim = len(spin_data) * 2

        for i_phi, phi in enumerate(list_of_phi):
            H_scattering = np.zeros((H_dim, H_dim))
            prev_E = None
            for i_l, l_data in enumerate(spin_data.values()):
                l_label = list(spin_data.keys())[i_l]
                for p in [0, 1]:
                    H_scattering[2 * i_l + p][2 * i_l + p] = l_data[p][i_phi]

                    if prev_E is not None:
                        scattering_coupling_0, scattering_coupling_1 = scattering_callable(prev_E, l_data[p][i_phi], tau, phi, spin_label, l_label)

                        H_scattering[2 * i_l + p][2 * i_l + p - 1] = scattering_coupling_0
                        H_scattering[2 * i_l + p - 1][2 * i_l + p] = scattering_coupling_1

                    if p == 1 and i_l > 0:
                        scattering_coupling_0, scattering_coupling_1 = scattering_callable(
                            H_scattering[2 * i_l + p - 3][2 * i_l + p -3], l_data[p][i_phi],
                            tau, phi, spin_label, l_label
                        )
                    
                        H_scattering[2 * i_l + p][2 * i_l + p - 3] = scattering_coupling_0
                        H_scattering[2 * i_l + p - 3][2 * i_l + p] = scattering_coupling_1

                    prev_E = l_data[p][i_phi]

            scattered_eigenvals, _ = np.linalg.eig(H_scattering)
            scattered_eigenvals = np.sort(scattered_eigenvals)

            for i, v in enumerate(scattered_eigenvals):
                results[spin_label][i][i_phi] = v
    
    return results



if __name__ == "__main__":
    phis = np.linspace(0, 2, num=101) * np.pi
    TAU = 0.95
    L = [0, ]
    res = get_uncoupled_ABS_eigvals(0.01, 0.01, phis, L)

    for spin, data in res.items():
        for l_label, l_data in data.items():
            plt.plot(phis, l_data[0], label=f"{l_label}L{spin}", ls="--", alpha=0.5, color="black")
            plt.plot(phis, l_data[1], label=f"{l_label}R{spin}", ls="--", alpha=0.5, color="gray")

    def test_callable(epsilon_0, epsilon_1, var_tau, phi, spin_label, l_label):
        T0 = 1 / (
            (1-epsilon_0**2) * (2/var_tau - 1)**2 + epsilon_0**2
        )
        T1 = 1 / (
            (1-epsilon_1**2) * (2/var_tau - 1)**2 + epsilon_1**2
        )
        R0 = 1 - T0
        R1 = 1 - T1
        return R0, R1

    res = get_coupled_ABS_eigvals(res, test_callable, TAU, phis, total_l=len(L)*2)
    
    for spin, data in res.items():
        if spin == 1:
            color = "blue"
        else:
            color = "red"
        for d in data:
            plt.plot(phis, d, color=color)
    
    plt.show()
    plt.close()