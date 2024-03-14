import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt

DELTA = 60e-6
HBAR = 1.0546e-34
E = 1.6022e-19

HBAR_OVER_E = HBAR / E

V_F = 1e3
d = 100e-9

omega = V_F / d
l = 0

def particle_like(phi, energy):
    return HBAR_OVER_E * omega * (phi * 0.5 - np.arcsin(energy/DELTA) + np.pi * (-(l+1) + 0.5)) - energy

def hole_like(phi, energy):
    return - HBAR_OVER_E * omega * (phi * 0.5 + np.arcsin(energy/DELTA) - np.pi * (l + 0.5)) - energy


N = 50
Phi = np.pi * np.linspace(0, 2, num=N)
E = []
E_h = []

for p in Phi:
    res, _ = opt.curve_fit(
        particle_like, [p, ], [0, ], p0=[0]
    )
    E.append(res[0])
    res, _ = opt.curve_fit(
        hole_like, [p, ], [0, ], p0=[0]
    )
    E_h.append(res[0])


plt.plot(Phi, E)
plt.plot(Phi, E_h)
plt.show()
