import numpy as np

u_diag = np.array([
    [0, 0],
    [1, 0]
])
d_diag = np.array([
    [0, 1],
    [0, 0]
])

up_d_dag = np.kron(np.eye(2), u_diag) 
up_d = np.kron(np.eye(2), d_diag)

down_d_dag = np.kron(u_diag, np.eye(2))
down_d = np.kron(d_diag, np.eye(2))

n_up = np.matmul(up_d_dag, up_d)
n_down = np.matmul(down_d_dag, down_d)

def get_H_tot(xi, gamma, U):
    H_dot = (xi - U) * (np.matmul(up_d_dag, up_d) + np.matmul(down_d_dag, down_d))

    phi = 0
    D = 10
    gap = 1
    gamma_phi = np.arctan(D/gap) * np.cos(phi/2) * gamma * 2 / np.pi
    # print(gamma, gamma_phi)

    H_t = -gamma_phi * (
        np.matmul(up_d_dag, down_d_dag) + 
        np.matmul(down_d, up_d)
    )

    H_sc = 0.5 * U * (
        np.matmul(n_down, n_down) + 
        np.matmul(n_up, n_up) + 
        np.matmul(n_down, n_up) + np.matmul(n_up, n_down) + 
        np.eye(4)
    )
    
    # print(H_t)
    return H_dot + H_t + H_sc


U = 1
g_arr = np.arange(0, 1, 0.05)
xi_arr = np.arange(-1, 1, 0.05)

res = np.empty((g_arr.size, xi_arr.size))

for i, _g in enumerate(g_arr):
    # print(_g)
    for j, _xi in enumerate(xi_arr):
        _H = get_H_tot(_xi, _g, U)
        # print(_H)
        evals, evecs = np.linalg.eig(_H)
        # print(_g, _xi)
        # print(evals)
        # print(evecs)

        if min(evals[0], evals[1]) < evals[2]:
            # Singlet
            res[i][j] = 1
        else:
            res[i][j] = 0
        
        # print(_g, _xi, evals)
        # print(evals, evecs)

import matplotlib.pyplot as plt

print(res)
plt.pcolormesh(xi_arr, g_arr, res)
plt.show()