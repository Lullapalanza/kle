import numpy as np

"""
Assume no spin physics?
"""

op_create = np.array([
    [0, 0],
    [1, 0]
])
op_destroy = np.array([
    [0, 1],
    [0, 0]
])

d_dag = op_create
d = op_destroy

n = np.matmul(d_dag, d)

# Bases are dot0, dot1, resonator (howmany?)
N_res = 2
a_dag = np.diag(np.sqrt(1 + np.arange(N_res-1)), -1)
a = np.diag(np.sqrt(1 + np.arange(N_res-1)), 1)

PLANCK = 4.136e-15 # eV
def get_H_tot(xi0, xi1, f, g):
    H_dot_0 = np.kron(xi0 * n, np.kron(np.eye(2), np.eye(N_res)))
    H_dot_1 = np.kron(np.kron(np.eye(2), xi1 * n), np.eye(N_res))

    H_res = f * PLANCK * np.kron(np.eye(4), np.diag(np.arange(N_res) + 0.5))

    tunnel = np.kron(
        d_dag, np.eye(2)
    ) + np.kron(
        np.eye(2), d
    )

    H_coupling = PLANCK * g * np.matmul(
        np.kron(np.eye(4), a_dag + a),
        np.kron(tunnel + np.transpose(tunnel), np.eye(N_res))
    )

    return H_dot_0 + H_dot_1 + H_res + H_coupling



import matplotlib.pyplot as plt
g = 100e6

lines = [list() for _ in range(4 * N_res)]
for _xi1 in np.arange(0, 1, 0.001) * 100e-6:
    _H = get_H_tot(_xi1, _xi1 + PLANCK * 6e9, 6e9, g)
    evals, evecs = np.linalg.eigh(_H)
    for i in range(len(lines)):
        lines[i].append(evals[i] / PLANCK)

for d in lines:
    plt.plot(np.arange(0, 1, 0.001) * 100e-6, d)
plt.show()
