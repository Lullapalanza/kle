import numpy as np
import matplotlib.pyplot as plt

# Sss, I want to simulate the dispersive shift as a function of circuit parameters, potentially optimizing
# Maybe at some point with dissipation for limits on Qi

PLANK = 6.62607e-34 # SI units
E = 1.6022e-19
SC_GAP = 50e-6

def cav_phase_zpf(Z):
    return 0.5 * np.sqrt(PLANK * Z / np.pi)

print(cav_phase_zpf(100), cav_phase_zpf(50))


def M(i, sigma):
    # TODO make a proper calculation here?
    state_coupling = {
        -2: {
            "up": 1,
            "down": 1
        },
        -1: {
            "up": 1,
            "down": 1
        },
        1: {
            "up": 1,
            "down": 1
        },
        2: {
            "up": 1,
            "down": 1
        },
    }

    return state_coupling[i][sigma]

def E(i, sigma):
    # TODO again do this properly, there is also phase relation
    spin_split = 0 # 100e6 # For now?

    state_E = {
        1: {
            "up": 2e9 + spin_split, # Hz?
            "down": 2e9 - spin_split
        }
        2: {
            "up": 5e9 + spin_split,
            "down": 5e9 - spin_split,
        }
    }

    return state_E[i][sigma]

