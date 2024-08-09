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

def get_H_tot(phi, xi, gamma, U, E_Z):
    H_dot = (xi - U) * (np.matmul(up_d_dag, up_d) + np.matmul(down_d_dag, down_d))

    D = 1000
    gap = 0.2
    gamma_phi = 2 * np.arctan(D/gap) * np.cos(phi/2) * gamma * 2 / np.pi
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
    
    H_EZ = 0.5 * E_Z * (np.matmul(up_d_dag, up_d) - np.matmul(down_d_dag, down_d))
    
    # return H_dot + H_t + H_sc + H_EZ

    # Pretending there is some junction phi dependence
    T = 0.01
    E_J = xi * (1 - (gap / U) * np.sqrt(1 - T * np.power(np.sin(phi/2), 2)))
    H_dot = (E_J - U) * (np.matmul(up_d_dag, up_d) + np.matmul(down_d_dag, down_d))
    return H_dot + H_t + H_sc + H_EZ

def get_states(evals, evecs):
    """
    return the state energies and avg charge
    [
        (), ...
        S, S, D, D
    ]
    """
    MIN_ERR = 1e-3
    result = [None, None, None, None]

    # print(evals)
    # print(evecs)

    for i, v in enumerate(evals):
        vec = evecs[:,i]
        "doublet"
        if abs(vec[1]) > MIN_ERR:
            result[2] = (v, 1)
        elif abs(vec[2]) > MIN_ERR:
            result[3] = (v, 1)
        
        else:
            if result[0] is None:
                result[0] = (v, 2 * vec[0]**2)
            else:
                result[1] = (evals[i], 2 * vec[0]**2)

    # print(result)

    if result[0][0] > result[1][0]:
        result[0], result[1] = result[1], result[0]
    
    if result[2][0] > result[3][0]:
        result[2], result[3] = result[3], result[2]
    
    return result

U = 1
phi = 3.1
g_arr = np.arange(0, 1, 0.01)
xi_arr = np.arange(-1, 1, 0.01)

res = np.empty((g_arr.size, xi_arr.size))

for i, _g in enumerate(g_arr):
    for j, _xi in enumerate(xi_arr):
        _H = get_H_tot(phi, _xi, _g, U, 0)
        evals, evecs = np.linalg.eig(_H)
        
        # print(evals, evecs)
        states = get_states(evals, evecs)
        # print(states)

        if states[0][0] <= states[2][0]:
            """
            Singlet
            """
            res[i][j] = states[0][1]
        else:
            res[i][j] = 1
        
        # print(_g, _xi, evals)
        # print(evals, evecs)

import matplotlib.pyplot as plt

plt.pcolormesh(xi_arr, g_arr, res)
plt.show()
plt.close()


# Take some values and get phi dependence

phi = np.arange(-1, 1, 0.01) * 2 * np.pi


a, b, c, d = [], [], [], []
for p in phi:
    _H = get_H_tot(p, -0.4, 0.2, 1, 0)
    evals, evecs = np.linalg.eig(_H)
    states = get_states(evals, evecs)
    
    a.append(states[0][0])
    b.append(states[1][0])
    c.append(states[2][0])
    d.append(states[3][0])

plt.plot(phi, a, label="S")
plt.plot(phi, b, label="S")
plt.plot(phi, c, label="D")
plt.plot(phi, d, label="D")
plt.legend()
plt.show()