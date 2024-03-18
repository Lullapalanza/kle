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


TAU = 0.95
LAMBDA1 = 2.25
LAMBDA2 = 1.75

# List of phi
N_PHI = 100
PHI = np.pi * np.linspace(0, 2, num=N_PHI)

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


def get_eigenenergies_of_ABS():
    # RUN CALC
    ENERGIES_D = [
        [], # +1
        [], # -1
        [], # +2
        [], # -2
    ]

    ENERGIES_U = [
        [], # +1
        [], # -1
        [], # +2
        [], # -2
    ]

    # For every phi
    for p in PHI:
        # results for -1 sign
        E_minus = get_energies_for_p(p, TAU, LAMBDA1, LAMBDA2, -1)
        # Now find energy of -1 level
        id_e1 = find_id_e1(E_minus)

        ENERGIES_D[0].append(E_minus[id_e1])
        ENERGIES_D[1].append(E_minus[id_e1-1])
        ENERGIES_D[2].append(E_minus[id_e1+1] if id_e1+1 < len(E_minus) else np.nan)
        ENERGIES_D[3].append(E_minus[id_e1-2] if id_e1-2 >= 0 else np.nan)

        E_plus = get_energies_for_p(p, TAU, LAMBDA1, LAMBDA2, 1)
        # Now find energy of -1 level
        id_e1 = find_id_e1(E_plus)

        ENERGIES_U[0].append(E_plus[id_e1])
        ENERGIES_U[1].append(E_plus[id_e1-1])
        ENERGIES_U[2].append(E_plus[id_e1+1] if id_e1+1 < len(E_plus) else np.nan)
        ENERGIES_U[3].append(E_plus[id_e1-2] if id_e1-2 >= 0 else np.nan)
    return ENERGIES_D, ENERGIES_U

ENERGIES_D, ENERGIES_U = get_eigenenergies_of_ABS()

for i, (ed, eu) in enumerate(zip(ENERGIES_D, ENERGIES_U)):
    if i == 0:
        plt.plot(PHI, ed, color="blue", label="d")
        plt.plot(PHI, eu, color="red", label="u", ls="--")
    else:
        plt.plot(PHI, ed, color="blue")
        plt.plot(PHI, eu, color="red", ls="--")

plt.ylabel(r"$\epsilon / \Delta$")
plt.xlabel(r"$\phi$")
plt.legend(
    bbox_to_anchor=(1, 1),
    title=r"$\tau =" + f"{TAU}" + r"$" + "\n" + r"$\lambda_1=" + f"{LAMBDA1}" + r"$" + "\n" + r"$\lambda_2=" + f"{LAMBDA2}" + r"$" 
)

plt.xlim(0, 2 * np.pi)
plt.axhline(-1, ls="--", color="gray")
plt.axhline(1, ls="--", color="gray")
plt.tight_layout()


plt.show()
        