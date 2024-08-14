import numpy as np
import matplotlib.pyplot as plt
from kle.calculations.two_leads_ZBW import get_H

U = 1
Delta = 1
E_Z = 0.0
xi = -0.3
gamma = 0.2

P = np.arange(-2, 2, 0.02) * np.pi
states = [list() for _ in range(3)]
for p in P:
    _xi = xi - U/2
    _H = get_H(p, _xi, gamma, U, Delta, E_Z)
    
    evals, evecs = np.linalg.eigh(_H)

    for i in range(len(states)):
        states[i].append(evals[i])


for s in states:
    plt.plot(P, s)
plt.show()