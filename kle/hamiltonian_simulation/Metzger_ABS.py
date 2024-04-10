import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt


def equation_B12(epsilon, phi, tau, lambda1, lambda2, sign: int):
    """
    Equation B12 from M2021, energy (epsilon) as ratio of gap
    """
    return tau * np.cos(
        (lambda1 - lambda2) * epsilon + sign * phi
    ) + (1 - tau) * np.cos(
        (lambda1 + lambda2) * epsilon
    ) - np.cos(
        2 * np.arccos(epsilon) - (lambda1 + lambda2) * epsilon
    )

# Params for energy sweep for eigenvalues
N_E0 = 23
E0s = np.linspace(-1, 1.1, num=N_E0)
E_DIFF_TOL = 1e-6

def find_id_e1(array):
    idx = np.abs(array).argmin()
    if array[idx] > 0:
        return idx
    else:
        return idx + 1


def get_energies_for_p(*args):
    _E = []
    for e0 in E0s:
        res = opt.root(equation_B12, e0, args=args)
        if not res.success:
            continue
        
        ei = res.x[0]
        add = True
        for e in _E:
            if np.abs(ei - e) < E_DIFF_TOL:
                add = False
                break
        
        if add:
            _E.append(ei)

    return np.sort(_E) # Sorted energies in ascending order


def get_coupled_Metzger_ABS(tau, lambda_1, lambda_2, list_of_phi, list_of_l):
    """
    Using equation from Metzger
    """
    def _get_new_arr(length):
        _new_arr = np.empty(length)
        _new_arr[:] = np.nan
        return _new_arr

    results = {
        -1: { # spin
            l: [
                _get_new_arr(len(list_of_phi)), # lower E
                _get_new_arr(len(list_of_phi)) # higher E
            ] for l in list_of_l
        },
        1: {
            l: [
                _get_new_arr(len(list_of_phi)),
                _get_new_arr(len(list_of_phi))
            ] for l in list_of_l
        }
    }

    # For every phi
    for i_phi, p in enumerate(list_of_phi):
        # results for -1 sign
        E_minus = get_energies_for_p(p, tau, lambda_1, lambda_2, -1)
        # Now find energy of -1 level
        id_e1 = find_id_e1(E_minus)

        for l in list_of_l:
            results[-1][l][0][i_phi] = E_minus[id_e1 + l*2 - 1]
            results[-1][l][1][i_phi] = E_minus[id_e1 + l*2]

        E_plus = get_energies_for_p(p, tau, lambda_1, lambda_2, 1)
        # Now find energy of -1 level
        id_e1 = find_id_e1(E_plus)

        for l in list_of_l:
            results[1][l][0][i_phi] = E_plus[id_e1 + l*2 - 1]
            results[1][l][1][i_phi] = E_plus[id_e1 + l*2]
    
    return results

if __name__ == "__main__":
    phis = np.linspace(0, 2, num=201) * np.pi
    TAU = 0.95

    res = get_coupled_Metzger_ABS(TAU, 3, 4, phis, list_of_l=[-1, 0, 1])
    
    for spin, data in res.items():
        if spin == 1:
            color = "blue"
        else:
            color = "red"
        for l_label, l_data in data.items():
            for e_p in l_data:
                plt.plot(phis, e_p, color=color)
    
    plt.show()
    plt.close()
            