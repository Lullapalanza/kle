import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt
from kle.andreev_bound_states import get_eigenenergies_of_ABS, PHI, N_PHI




def labeled_current_ABS(epsilon, phi, l, lambda_sum, lambda_diff, p, sigma):
    return (2 * p / lambda_sum) * (
        sigma * 0.5 * epsilon * lambda_diff + phi/2 - p * np.arcsin(epsilon) + np.pi * (p * l - 0.5)
    ) - epsilon


LAMBDA_SUM = 0.5
LAMBDA_DIFF = 0.3

# List of phi
N_PHI = 401
PHI = np.pi * np.linspace(0, 2, num=N_PHI)
# PHI = np.pi * np.array([1])

# E_m1m = []
# E_m1p = []
E_011 = []
E_01m1 = []

E_0m11 = []
E_0m1m1 = []
# E_1m = []
# E_1p = []

for p in PHI:
    args = (p, 0, LAMBDA_SUM, LAMBDA_DIFF, 1, 1)
    res_p = opt.root(labeled_current_ABS, 0.1, args=args, method="hybr", options={"factor": 1})
    if res_p.success:
        E_011.append(res_p.x[0])
    else:
        E_011.append(np.nan)

    args = (p, 0, LAMBDA_SUM, LAMBDA_DIFF, 1, -1)
    res_p = opt.root(labeled_current_ABS, -0.1, args=args, method="hybr", options={"factor": 1})
    if res_p.success:
        E_01m1.append(res_p.x[0])
    else:
        E_01m1.append(np.nan)

    args = (p, 0, LAMBDA_SUM, LAMBDA_DIFF, -1, 1)
    res_m = opt.root(labeled_current_ABS, -0.1, args=args, method="hybr", options={"factor": 1})
    if res_m.success:
        E_0m11.append(res_m.x[0])
    else:
        E_0m11.append(np.nan)
    
    args = (p, 0, LAMBDA_SUM, LAMBDA_DIFF, -1, -1)
    res_m = opt.root(labeled_current_ABS, 0.1, args=args, method="hybr", options={"factor": 1})
    if res_m.success:
        E_0m1m1.append(res_m.x[0])
    else:
        E_0m1m1.append(np.nan)


tau = 0.95
DELTA = 1 # ueV

def get_R(epsilon_0, epsilon_1, var_tau):
    T = 1 / (
        (1-epsilon_0**2) * (2/var_tau - 1)**2 + epsilon_0**2
    )
    R = 1 - T
    return R

def get_labeled_eigenenergies_of_ABS():
    return E_011, E_01m1, E_0m11, E_0m1m1

def get_labeled_s_eigenenergies_of_ABS():
# Now for some fudge
    scattered_E011 = []
    scattered_E01m1 = []

    scattered_E0m11 = []
    scattered_E0m1m1 = []


    def scattering(epsilon_0, epsilon_1, var_tau):
        T0 = 1 / (
            (1-epsilon_0**2) * (2/var_tau - 1)**2 + epsilon_0**2
        )
        T1 = 1 / (
            (1-epsilon_1**2) * (2/var_tau - 1)**2 + epsilon_1**2
        )
        print(T0, T1)
        
        R0 = 1 - T0
        R1 = 1 - T1
        
        H_scattering = np.array([
            [epsilon_0, R1],
            [R0, epsilon_1]
        ])
        print(H_scattering)
        eigvals, _ = np.linalg.eig(H_scattering)
        eigvals = np.sort(eigvals)
        
        return eigvals[0], eigvals[1]


    for i in range(len(PHI)):
        print("PHI:", PHI[i])
        sc1, sc2 = scattering(E_011[i], E_0m11[i], tau)

        scattered_E011.append(sc1)
        scattered_E0m11.append(sc2)

        sc3, sc4 = scattering(E_01m1[i], E_0m1m1[i], tau)

        scattered_E01m1.append(sc3)
        scattered_E0m1m1.append(sc4)
    
    return scattered_E011, scattered_E01m1, scattered_E0m11, scattered_E0m1m1

if __name__ == "__main__":
    # plt.plot(PHI, E_011, label="011")
    # plt.plot(PHI, E_01m1, label="01m1")
    # plt.plot(PHI, E_0m11, label="0m11")
    # plt.plot(PHI, E_0m1m1, label="0m1m1")
    scattered_E011, scattered_E01m1, scattered_E0m11, scattered_E0m1m1 = get_labeled_s_eigenenergies_of_ABS()

    plt.plot(PHI, scattered_E011, label="up")
    plt.plot(PHI, scattered_E0m11, label="up")
    plt.plot(PHI, scattered_E01m1, label="down")
    plt.plot(PHI, scattered_E0m1m1, label="down")


    plt.axhline(-1 * DELTA, ls="--", color="gray")
    plt.axhline(1 * DELTA, ls="--", color="gray")

    ENERGIES_D, ENERGIES_U = get_eigenenergies_of_ABS(tau)
    for i, (ed, eu) in enumerate(zip(ENERGIES_D, ENERGIES_U)):
        if i == 0:
            plt.plot(PHI, np.array(ed) * DELTA, color="blue", label="d", ls="--")
            plt.plot(PHI, np.array(eu) * DELTA, color="red", label="u", ls="--")
        else:
            plt.plot(PHI, np.array(ed) * DELTA, color="blue", ls="--")
            plt.plot(PHI, np.array(eu) * DELTA, color="red", ls="--")

    plt.ylabel(r"$\epsilon / \Delta$")
    plt.xlabel(r"$\phi$")
    plt.legend(
        bbox_to_anchor=(1, 1),
        title=r"$\tau =" + f"{tau}" + r"$" + "\n" + r"$\lambda_1=" + f"{0.4}" + r"$" + "\n" + r"$\lambda_2=" + f"{0.1}" + r"$" 
    )
    plt.xlim(0, 2 * np.pi)
    plt.tight_layout()
    plt.show()
