import numpy as np



lu = {'0':0, 'u':1, 'd':2, '2':3} # label to index lookup table

def to_index(s):
    return lu[s[0]]*4 + lu[s[1]]

def to_inds(tp):
    return to_index(tp[0]), to_index(tp[1])

state_vectors = [ #|n_SC, n_N first SC then QD
    r'$|0,0\rangle$', r'$|\uparrow,0\rangle$', r'$|\downarrow,0\rangle$', r'$|2,0\rangle$'
    r'$|0,\uparrow \rangle$', r'$|\uparrow,\uparrow \rangle$', r'$|\downarrow,\uparrow \rangle$', r'$|2,\uparrow \rangle$',
    r'$|0,\downarrow \rangle$', r'$|\uparrow,\downarrow \rangle$', r'$|\downarrow,\downarrow \rangle$', r'$|2,\downarrow \rangle$',
    r'$|0,2\rangle$', r'$|\uparrow,2\rangle$', r'$|\downarrow,2\rangle$', r'$|2,2\rangle$'
] 

t_term_names = [('0u', 'u0'), ('u0', '0u'), ('0d', 'd0'), ('d0', '0d'), # The 16 hamiltonian using the 4 prominent states
                ('2u', 'u2'), ('u2', '2u'), ('2d', 'd2'), ('d2', '2d'),
                ('ud', '02'), ('02', 'ud'), ('ud', '20'), ('20', 'ud'),
                ('du', '02'), ('02', 'du'), ('du', '20'), ('20', 'du')]

t_terms = list(map(to_inds, t_term_names))


n_bare = np.array([0,1,1,2])
    
n_vec = (n_bare[None,:] + n_bare[:,None]).ravel()
def sep_even_odd(mat):
    mat_e = mat[n_vec%2==0][:,n_vec%2==0]
    mat_o = mat[n_vec%2==1][:,n_vec%2==1]
    return mat_e, mat_o

n_sum = np.diag(n_vec)
n_qd = np.kron(np.diag([0,1,1,2]), np.eye(4))
n_qd_e, n_qd_o = sep_even_odd(n_qd)

def get_charge_e(ket0):
    return ket0[None,:] @ n_qd_e @ ket0[:,None]

def get_charge_o(ket0):
    return ket0[None,:] @ n_qd_o @ ket0[:,None]

def smallest_2args(arr):
    ind_min = np.argmin(arr)
    ind_2min = np.argwhere(arr==np.partition(arr,1)[1])[0,0]
    return np.sort([ind_min,ind_2min])

def block_diag_ZBW(mu, EZ_QD, EZ_SC, U, Delta, t):

    normal_qd = np.kron(np.array([[0,0,0,0], [0,mu+EZ_QD,0,0], [0,0,mu-EZ_QD,0], [0,0,0,2*mu+U]]), np.eye(4))
    super_qd = np.kron(np.eye(4), np.array([[0,0,0,Delta], [0,EZ_SC,0,0], [0,0,-EZ_SC,0], [Delta,0,0,0]]))

    ham = normal_qd + super_qd
    for t_ind in t_terms:
        ham[t_ind] = t

    ham_e, ham_o = sep_even_odd(ham)
    
    vals_e, vecs_e = np.linalg.eigh(ham_e)
    vals_o, vecs_o = np.linalg.eigh(ham_o)
    
    return vals_e, vecs_e, vals_o, vecs_o, ham

EZ_QD=0
EZ_SC=0

Delta0 = 75e-3 # 77.5ueV
Bc = 0.911
b = 0.35
U = 1.6 #1.6e-3 1mV charging
Delta = Delta0*np.sqrt(1-b/Bc)
t = 0.11 #25e-6 tunnel coupliong
mu = -0.1
mus = -1

_h = block_diag_ZBW(
    mu, EZ_QD, EZ_SC, U, Delta, t
)




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

gv = np.array([[1], [0]])
ev = np.array([[0], [1]])

gg = np.kron(gv, gv) # GG
eg = np.kron(ev, gv) # spin down excitation
ge = np.kron(gv, ev) # spin up
ee = np.kron(ev, ev) # Both

def get_H(xi, gamma, U, DELTA, phi=3.14):
# For the Dot
    # print("INH", xi, gamma)
    H_dot = np.kron(
        xi * (n_up + n_down) + U * np.matmul(n_down, n_up),
        np.eye(4)
    )

    # Superconductor
    H_sc = np.kron(
        np.eye(4),
        DELTA * (np.matmul(up_d_dag, down_d_dag) + np.matmul(down_d, up_d))
    )

    # Tunneling
    H_t = gamma * (
        np.kron(up_d_dag, up_d) + np.kron(up_d, up_d_dag) +
        np.kron(down_d_dag, down_d) + np.kron(down_d, down_d_dag)
    )

    H_total = H_dot + H_sc + H_t
    # evals, evecs = np.linalg.eig(H_total)
    # print(evals, evecs)
    
    return H_total


e_dot = np.kron(np.diag([0, 1, 1, 2]), np.eye(4))

e_tot = np.kron(np.diag([0, 1, 1, 2]), np.eye(4)) + np.kron(np.eye(4), np.diag([0, 1, 1, 2]))

def get_state_dot_charge(state):
    res = state.dot(e_dot).dot(state)
    # res = state.dot(e_tot).dot(state)
    return res

H = get_H(0, 0, 1, 1)
evals, evecs = np.linalg.eig(H)

i_min = np.argmin(evals)
s_min = evecs[:,i_min]


Delta0 = 75e-3 # 77.5ueV
Bc = 0.911
b = 0.35
U = 1.6 #1.6e-3 1mV charging
Delta = Delta0*np.sqrt(1-b/Bc)
t = 0.11 #25e-6 tunnel coupliong
mus = -1

# _H = get_H(mu, t, U, Delta)
# print(_H)
# evals, evecs = np.linalg.eig(_H)
# print(evecs.size)
# for i, val in enumerate(evals):
#     _v = evecs[:,i]
#     _v[np.abs(_v) < 0.01] = 0 
#     print(val, _v)
#     print(get_state_dot_charge(evecs[:,i]))

# print(sum(_H == _h))


# BLALGAL
n_bare = np.array([0,1,1,2])

n_vec = (n_bare[None,:] + n_bare[:,None]).ravel()
n_sum = np.diag(n_vec)

def sep_even_odd(mat):
    mat_e = mat[n_vec%2==0][:,n_vec%2==0]
    mat_o = mat[n_vec%2==1][:,n_vec%2==1]
    return mat_e, mat_o
# AASAF


U = 1
Delta = 1
phi = 0
g_arr = np.arange(0, 1, 0.02)
xi_arr = np.arange(-1, 1, 0.02)
res = np.empty((g_arr.size, xi_arr.size))

rese = np.empty((g_arr.size, xi_arr.size))
reso = np.empty((g_arr.size, xi_arr.size))
resoo = np.empty((g_arr.size, xi_arr.size))

for i, _g in enumerate(g_arr):
    for j, _xi in enumerate(xi_arr):
        _xi = _xi - U/2
        _H = get_H(_xi, _g, U, Delta)
        evals, evecs = np.linalg.eig(_H)

        vals_e, vecs_e, vals_o, vecs_o, _h = block_diag_ZBW(_xi, 0, 0, U, Delta, _g)
        charges_e = get_charge_e(vecs_e[:,0])
        charges_o = get_charge_o(vecs_o[:,0])

        # print("B", _xi, _g)
        # print(_H)
        # print(_h)
        # print("sep", vals_e, vals_o)
        # # print(charges_e, charges_o)
        # print("tot", evals)

        np.linalg.eig(_H)
        
        ind = np.argsort(evals)
        evecs = evecs[:,ind]
        evals = evals[ind]

        _v = evecs[:,0]
        
        res[i][j] = get_state_dot_charge(_v)
        rese[i][j] = charges_e[0][0]
        reso[i][j] = charges_o[0][0]

        if vals_e[0] < vals_o[0]:
            resoo[i][j] = charges_e[0][0]
        else:
            resoo[i][j] = charges_o[0][0]

import matplotlib.pyplot as plt

plt.pcolormesh(xi_arr, g_arr, res)
plt.colorbar()
plt.show()


plt.pcolormesh(xi_arr, g_arr, rese)
plt.colorbar()
plt.show()

plt.pcolormesh(xi_arr, g_arr, reso)
plt.colorbar()
plt.show()

plt.pcolormesh(xi_arr, g_arr, resoo)
plt.colorbar()
plt.show()
plt.close()
