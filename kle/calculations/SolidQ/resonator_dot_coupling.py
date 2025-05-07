import numpy as np
import matplotlib.pyplot as plt

# ===== Base conctruction ====
op_create = np.array([
    [0, 0],
    [1, 0]
])
op_destroy = np.array([
    [0, 1],
    [0, 0]
])
# ===== up and down spin states =====
up_d_dag = np.kron(np.eye(2), op_create)
up_d = np.kron(np.eye(2), op_destroy)

down_d_dag = np.kron(op_create, np.eye(2))
down_d = np.kron(op_destroy, np.eye(2))

n_up = np.matmul(up_d_dag, up_d)
n_down = np.matmul(down_d_dag, down_d)

# ==== dot ====
DOT_DIM = 4
_H_xi = n_up + n_down
_H_U = np.matmul(n_down, n_up)
E = 1.6e-19

# === Resonator ====
RES_DIM = 4
res_a = np.diag(np.sqrt(np.arange(1, RES_DIM)), 1)
res_a_dagger = np.diag(np.sqrt(np.arange(1, RES_DIM)), -1)

HBAR = 1e-34

def get_H(xi, U, E_Z, omega, g):
    H_dot = np.kron(
        xi * _H_xi + U * _H_U + 0.5 * E_Z * (n_up - n_down),
        np.eye(RES_DIM)
    ) # 4 dim

    H_res = np.kron(
        np.eye(DOT_DIM),
        HBAR * omega * np.matmul(res_a_dagger, res_a)
    )

    H_int = -1.j * g * np.matmul(
        np.kron(np.eye(DOT_DIM), (res_a - res_a_dagger)),
        np.kron(_H_xi, np.eye(RES_DIM))
    )

    return H_dot + H_res + H_int


e_dot = np.kron(np.diag([0, 1, 1, 2]), np.eye(RES_DIM))
def get_state_dot_charge(state):
    res = np.conjugate(state).dot(e_dot).dot(state)
    return res

GHZ_TO_EV = 4.136e-6

if __name__ == "__main__":
    # fig, ax = plt.subplots(1, figsize=(10, 8))

    E_Z = 0.1 * GHZ_TO_EV * E
    U = 200 * GHZ_TO_EV # V
    OMEGA = 2 * np.pi * 6e9
    __xi = 5 * GHZ_TO_EV

    print(U * E / (2e9 * np.pi * HBAR))

    g_arr = np.arange(0, 1, 0.02) * 10e9
    states = [list() for _ in range(8)]
    disp_shift = []

    for i, _g in enumerate(g_arr):
        _xi = __xi

        _H = get_H(_xi * E, U * E, E_Z, OMEGA, _g * HBAR)
        evals, evecs = np.linalg.eigh(_H/(2 * np.pi * HBAR))
        _v = evecs[:,0] # Take the smallest eigenvalue eigenvector - ground state            
        # res_charge[i][j] = get_state_dot_charge(_v)
        # print(evals - evals[0])
        _evals = evals - evals[0]
        print(_evals)
        # print("g:", _g,"res 0:", _evals[1], "res 1:", _evals[4]-_evals[3])
        disp_shift.append(_evals[4] - _evals[3] - _evals[1])
        for i in range(len(states)):
            states[i].append(evals[i] - evals[0])
        

    # pc0 = ax.pcolormesh(xi_arr, g_arr, res_charge)
    # fig.colorbar(pc0)
    for i, s in enumerate(states):
        plt.plot(g_arr, s)
    plt.show()
    plt.close()

    plt.plot(g_arr, disp_shift)
    plt.xlabel("g (Hz)")
    plt.ylabel("Dispersive shift, change in resonance frequency (Hz)")
    plt.show()