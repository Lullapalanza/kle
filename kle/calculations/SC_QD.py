import numpy as np

u_diag = np.array([
    [0, 1],
    [0, 0]
])
d_diag = np.array([
    [0, 0],
    [1, 0]
])

up_d_dag = np.kron(np.eye(2), u_diag) 
up_d = np.kron(np.eye(2), d_diag)

down_d_dag = np.kron(u_diag, np.eye(2))
down_d = np.kron(d_diag, np.eye(2))

n_up = np.matmul(up_d_dag, up_d)
n_down = np.matmul(down_d_dag, down_d)

def get_H_tot(xi, gamma, U):
    H_dot = xi * (np.matmul(up_d_dag, up_d) + np.matmul(down_d_dag, down_d))

    H_t = -gamma * np.matmul(up_d_dag, down_d_dag)

    H_sc = 0.5 * U * (
        np.matmul(n_down, n_down) + 
        np.matmul(n_up, n_up) + 
        np.matmul(n_down, n_up) + np.matmul(n_up, n_down) + 
        np.eye(4)
    )
    
    print(H_t)
    return H_dot + H_t + H_sc


U = 1
g_arr = np.arange(0, 1, 0.1)
xi_arr = np.arange(-1, 1, 0.1)

for _g in g_arr:
    print(_g)
    for _xi in xi_arr:
        _H = get_H_tot(_xi, _g, U)
        # print(_H)
        evals, evecs = np.linalg.eig(_H)
        
        # print(evals)
        # print(evals, evecs)