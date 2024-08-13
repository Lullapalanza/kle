import numpy as np
import matplotlib.pyplot as plt

# ===== Base construction stuff for matrixes =====
op_create = np.array([
    [0, 0],
    [1, 0]
])
op_destroy = np.array([
    [0, 1],
    [0, 0]
])

# ===== Up and Down spin states =====
up_d_dag = np.kron(np.eye(2), op_create)
up_d = np.kron(np.eye(2), op_destroy)

down_d_dag = np.kron(op_create, np.eye(2))
down_d = np.kron(op_destroy, np.eye(2))

n_up = np.matmul(up_d_dag, up_d)
n_down = np.matmul(down_d_dag, down_d)

# ==== In this basis the states are =====
gv = np.array([[1], [0]])
ev = np.array([[0], [1]])

gg = np.kron(gv, gv) # GG
eg = np.kron(ev, gv) # EG
ge = np.kron(gv, ev) # GE
ee = np.kron(ev, ev) # EE

# ===== For the dot =====
_H_xi = n_up + n_down
_H_U = np.matmul(n_down, n_up)

# ==== Superconductor leads =====
_H_lead = np.matmul(up_d_dag, down_d_dag)
_H_lead_dag = np.transpose(np.conjugate(_H_lead))


def get_H(phi, xi, gamma, U, DELTA, E_Z=0):
    """
    Get hamiltonian for a SC - QD - SC system where all parts can have gg, eg, ge or ee states (only 1 orbital)
    """
    # For the Dot
    H_dot = np.kron(
        xi * _H_xi + U * _H_U + 0.5 * E_Z * (n_up - n_down),
        np.eye(16)
    )

    # Superconductor R
    H_sc_R = np.kron(
        np.eye(4),
        np.kron(
            np.eye(4),
            -DELTA * (_H_lead + _H_lead_dag)
        )
    )

    # SC L
    H_sc_L = np.kron(
        np.eye(4),
        np.kron(
            -DELTA * np.exp(-1.j * phi) * _H_lead -DELTA * np.exp(1.j * phi) * _H_lead_dag,
            np.eye(4)
        )
    )

    # Tunneling
    _H_R = np.kron(
            up_d_dag,
            np.kron(np.eye(4), up_d)
        ) + np.kron(
            down_d_dag,
            np.kron(np.eye(4), down_d)
        )
    H_t_R = gamma * (_H_R + np.transpose(np.conjugate(_H_R)))

    _H_L = np.kron(
        np.kron(up_d_dag, up_d) + np.kron(down_d_dag, down_d),
        np.eye(4)
    )
    H_t_L = H_t = gamma * (_H_L + np.transpose(np.conjugate(_H_L)))

    H_total = H_dot + H_sc_L + H_sc_R + H_t_L + H_t_R
    return H_total


e_dot = np.kron(np.diag([0, 1, 1, 2]), np.eye(16))
def get_state_dot_charge(state):
    res = np.conjugate(state).dot(e_dot).dot(state)
    return res



if __name__ == "__main__":
    fig, ax = plt.subplots(2)
    # Run some test
    U = 1
    Delta = 1

    phi0 = 0
    phi1 = np.pi

    # Ranges for 2D sweep
    g_arr = np.arange(0, 1, 0.02)
    xi_arr = np.arange(-1, 1, 0.02)
    res_phi0 = np.empty((g_arr.size, xi_arr.size))
    res_phi1 = np.empty((g_arr.size, xi_arr.size))

    for i, _g in enumerate(g_arr):
        for j, _xi in enumerate(xi_arr):
            _xi = _xi - U/2

            _H = get_H(phi0, _xi, _g, U, Delta)
            evals, evecs = np.linalg.eigh(_H)
            _v = evecs[:,0] # Take the smallest eigenvalue eigenvector - ground state            
            res_phi0[i][j] = get_state_dot_charge(_v)

            _H = get_H(phi1, _xi, _g, U, Delta)
            evals, evecs = np.linalg.eigh(_H)
            _v = evecs[:,0] # Take the smallest eigenvalue eigenvector - ground state
            res_phi1[i][j] = get_state_dot_charge(_v)

    ax[0].pcolormesh(xi_arr, g_arr, res_phi0)
    ax[1].pcolormesh(xi_arr, g_arr, res_phi1)
    # plt.colorbar()
    plt.show()
