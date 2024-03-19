import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt
from kle.andreev_bound_states import get_eigenenergies_of_ABS, PHI, N_PHI


def fudged_ABS(epsilon, phi, l, _lambda, _lambda_diff, sign):
    l = l if sign == -1 else (-l + 1)
    return 2 * sign * (sign * 0.5 * _lambda_diff * epsilon + phi/2 - sign * np.arcsin(epsilon) + np.pi * (-l + sign * 0.5))/_lambda - epsilon

def _fudged_ABS(epsilon, phi, l, lambda_sum, lambda_diff, p, sigma):
    return (2 * p / lambda_sum) * (
        p * sigma * 0.5 * epsilon * lambda_diff + phi/2 - p * np.arcsin(epsilon) + np.pi * (p * l - 0.5)
    ) - epsilon


LAMBDA1 = 2
LAMBDA2 = 0.1
# SHort
# LAMBDA1 = 0.2
# LAMBDA2 = 0.01
LAMBDA_SUM = 5
LAMBDA_DIFF = 0.5

# List of phi
N_PHI = 401
PHI = np.pi * np.linspace(0, 2, num=N_PHI)

# E_m1m = []
# E_m1p = []
E_0m = []
E_0p = []

E_0m_ = []
E_0p_ = []
# E_1m = []
# E_1p = []

for p in PHI:
    args = (p, 1, LAMBDA_SUM, LAMBDA_DIFF, 1, 1)
    res_p = opt.root(_fudged_ABS, 0.1, args=args, method="hybr", options={"factor": 1})
    if res_p.success:
        E_0m.append(res_p.x[0])
    else:
        E_0m.append(np.nan)

    args = (p, 1, LAMBDA_SUM, LAMBDA_DIFF, 1, -1)
    res_p = opt.root(_fudged_ABS, -0.1, args=args, method="hybr", options={"factor": 1})
    if res_p.success:
        E_0m_.append(res_p.x[0])
    else:
        E_0m_.append(np.nan)

    args = (p, 1, LAMBDA_SUM, LAMBDA_DIFF, -1, 1)
    res_m = opt.root(_fudged_ABS, -0.1, args=args, method="hybr", options={"factor": 1})
    if res_m.success:
        E_0p.append(res_m.x[0])
    else:
        E_0p.append(np.nan)
    
    args = (p, 1, LAMBDA_SUM, LAMBDA_DIFF, -1, -1)
    res_m = opt.root(_fudged_ABS, 0.1, args=args, method="hybr", options={"factor": 1})
    if res_m.success:
        E_0p_.append(res_m.x[0])
    else:
        E_0p_.append(np.nan)

# plt.plot(PHI, E_m1m, label="m1m")
# plt.plot(PHI, E_m1p, label="m1p")
plt.plot(PHI, E_0m, label="0m")
plt.plot(PHI, E_0p, label="0p")
plt.plot(PHI, E_0m_, label="0m_")
plt.plot(PHI, E_0p_, label="0p_")

# Now for some fudge
# fudged_E0 = []
# fudged_E1 = []

# fudged_E2 = []
# fudged_E3 = []

# def obf_scattering(epsilons, tau):
#     t_AB_0 = 1 / (2 * epsilons[0]**2 - 1 + (2/tau) * (1 - epsilons[0]**2))
#     t_AB_1 = 1 / (2 * epsilons[1]**2 - 1 + (2/tau) * (1 - epsilons[1]**2))
#     H_fudge = np.array([
#         [epsilons[0], (1 - t_AB_1**2)],
#         [(1 - t_AB_0**2), epsilons[1]]
#     ])
#     eigvals, _ = np.linalg.eig(H_fudge)
#     return epsilons - eigvals


# tau = 0.95
# for i in range(len(PHI)):
#     print(E_0m[i], E_0p[i])
#     t_AB_0 = 1 / (2 * E_0m[i]**2 - 1 + (2/tau) * (1 - E_0m[i]**2))
#     t_AB_1 = 1 / (2 * E_0p[i]**2 - 1 + (2/tau) * (1 - E_0p[i]**2))
#     H_fudge = np.array([
#         [E_0m[i], (1 - t_AB_0**2)],
#         [(1 - t_AB_1**2), E_0p[i]]
#     ])
#     eigvals, _ = np.linalg.eig(H_fudge)
#     eigvals = np.sort(eigvals)
#     # res_m = opt.root(obf_scattering, np.array([E_0m[i], E_0p[i]]), args=(tau), method="hybr", options={"factor": 1})


#     fudged_E0.append(eigvals[0])
#     fudged_E1.append(eigvals[1])

#     t_AB_0 = 1 / (2 * E_0m_[i]**2 - 1 + (2/tau) * (1 - E_0m_[i]**2))
#     t_AB_1 = 1 / (2 * E_0p_[i]**2 - 1 + (2/tau) * (1 - E_0p_[i]**2))
#     H_fudge = np.array([
#         [E_0m_[i], (1 - t_AB_0**2)],
#         [(1 - t_AB_1**2), E_0p_[i]]
#     ])
#     eigvals, _ = np.linalg.eig(H_fudge)
#     eigvals = np.sort(eigvals)
#     fudged_E2.append(eigvals[0])
#     fudged_E3.append(eigvals[1])


# plt.plot(PHI, fudged_E0)
# plt.plot(PHI, fudged_E1)
# plt.plot(PHI, fudged_E2)
# plt.plot(PHI, fudged_E3)
# plt.axhline(-1, ls="--", color="gray")
# plt.axhline(1, ls="--", color="gray")
# plt.legend()

# # plt.ylim(-0.35, 0.35)
# # plt.xlim(1.5, 2 * np.pi - 1.5)

ENERGIES_D, ENERGIES_U = get_eigenenergies_of_ABS()
for i, (ed, eu) in enumerate(zip(ENERGIES_D, ENERGIES_U)):
    if i == 0:
        plt.plot(PHI, ed, color="blue", label="d", ls="--")
        plt.plot(PHI, eu, color="red", label="u", ls="--")
    else:
        plt.plot(PHI, ed, color="blue", ls="--")
        plt.plot(PHI, eu, color="red", ls="--")

plt.show()
