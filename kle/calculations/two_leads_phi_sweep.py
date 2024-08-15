import numpy as np
import matplotlib.pyplot as plt
from kle.calculations.two_leads_ZBW import get_H

up_dot = np.kron(np.diag([0, 1, 0, 0]), np.eye(16))
def get_up(state):
    res = np.conjugate(state).dot(up_dot).dot(state)
    return res

down_dot = np.kron(np.diag([0, 0, 1, 0]), np.eye(16))
def get_down(state):
    res = np.conjugate(state).dot(down_dot).dot(state)
    return res


U = 1.6
Delta = 72e-3
E_Z = 0.001
xi = -0.75
gamma = 0.03
phi_so = 0.0
title = f"phisweep_v4"

pc_params = {"U": U, "Delta": Delta, "xi": xi, "gamma": gamma, "phi_so": phi_so, "EZ": E_Z}
def to_label(dict_of_params):
    label = ""
    for k, v in dict_of_params.items():
        label += f"{k} = {v:.3f}\n"
    return label


P = np.arange(-2, 2, 0.02) * np.pi
states = [list() for _ in range(2)]
lsss = ["-", "--", "-.", ":"]
for p in P:
    _xi = xi - U/2
    _H = get_H(p, _xi, gamma, U, Delta, E_Z, phi_so)
    
    evals, evecs = np.linalg.eigh(_H)

    for i in range(len(states)):
        states[i].append(evals[i])


plt.figure(figsize=(10, 6))

for i, s in enumerate(states):
    plt.plot(P, s, ls=lsss[i])

plt.xlabel(r"phase, $\phi (rad)$")
plt.ylabel(r"Energy")
plt.legend(title=to_label(pc_params), bbox_to_anchor=(1.0, 0.7))
plt.tight_layout()
plt.savefig(
    f"C:/Users/nbr720/Documents/PhD/design/SCQD_figs/{title}.png"
)
plt.savefig(
    f"C:/Users/nbr720/Documents/PhD/design/SCQD_figs/{title}.pdf"
)
