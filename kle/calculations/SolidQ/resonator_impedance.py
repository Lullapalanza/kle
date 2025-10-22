'''
Something something something, estimate impedance
'''
import numpy as np
import matplotlib.pyplot as plt

def get_Z_parallel_LC(omega, L, C):
    return (1/(omega * 1.j * L) + 1.j * omega * C)**(-1)


def get_Z_discreete_cpw(omega, Ltot, Ctot, n):
    Ll = Ltot/n
    Cl = Ctot/n

    new_imp = 1.j * omega * Ll + 1/(1.j * omega * Cl)
    for i in range(1, n):
        new_imp = 1.j * omega * Ll + (omega * 1.j * Cl + new_imp**(-1))**(-1)
    
    Cext = Ctot/100
    return (new_imp**(-1) + 1.j * omega * Cl)**(-1)


def get_Z_shunted_meander_res(omega, Ltot, Ctot, Cshort, n):
    Ll = Ltot/n
    Cl = Ctot/n
    Cshort = Cshort/n

    new_imp = (1/(1.j * omega * Ll) + 1.j * omega * Cshort)**(-1) + 1/(1.j * omega * Cl)
    for i in range(1, n):
        new_imp = (1/(1.j * omega * Ll) + 1.j * omega * Cshort)**(-1) + (omega * 1.j * Cl + new_imp**(-1))**(-1)
    
    return (new_imp**(-1) + 1.j * omega * Cl)**(-1)


def get_gnd_cap(omega, m, M, Cl):
    gnd_half = 1/(1.j * omega * Cl/2)
    gnd_halfm = 1/(1.j * omega * Cl/(2 * m))

    pass


def get_Z_crossC_meander_res(omega, Ltot, Ctot, Ccross, m, n):
    Ll = Ltot/n
    Cl = Ctot/n
    Ccross = Ccross/n

    print("Ccross vs Cl:", Ccross, Cl)

    gnd0 = 2/(1.j * omega * 1 * Cl)
    gnd1 = 2/(1.j * omega * 1 * Cl) + (m-1)/(1.j * omega * (Ccross + Cl/m)) # This is a bit fudged, need to imrpove this!
    gnd_tot = (gnd0**-1 + gnd1**-1)**-1
    
    new_imp = (1/(1.j * omega * Ll) + gnd_tot**-1)**(-1) + gnd_tot
    for j in range(m):
        gnd0 = 2/(1.j * omega * 1 * Cl) + (j)/(1.j * omega * Ccross)
        gnd1 = 2/(1.j * omega * 1 * Cl) + (m-j-1)/(1.j * omega * Ccross)
        gnd_tot = (gnd0**(-1) + gnd1**(-1))**(-1)
        for i in range(n//m):
            new_imp = 1.j * omega * Ll + (gnd_tot**(-1) + new_imp**(-1))**(-1)
    
    return (new_imp**(-1) + gnd_tot**(-1))**(-1)


if __name__ == "__main__":
    frequencies = np.linspace(5e9, 20e9, num=5000)

    mult_fac = 10

    Lp = 26.3e-9 * mult_fac
    Cp = 2.65e-14 / mult_fac
    print("Zratio:", (Lp/Cp)**0.5)

    parallel_Z = get_Z_parallel_LC(frequencies * 2 * np.pi, Lp, Cp)
    print("Lumped frequency (GHz)", (2e9*np.pi)**(-1)/(Lp*Cp)**0.5)

    Lcpw = Lp * np.pi
    Ccpw = Cp * np.pi
    cpw_Z = get_Z_discreete_cpw(frequencies * 2 * np.pi, Lcpw, Ccpw, 10000)
    print("CPW frequency (GHz):", 0.5e-9/(Lcpw*Ccpw)**0.5)

    # This never gets to a higher frequency
    Ccompare = 1e-10

    Cshort = Ccompare # 1e-10
    meander_Z = get_Z_shunted_meander_res(frequencies * 2 * np.pi, Lcpw, Ccpw, Cshort, 10000)

    plt.plot(frequencies, np.abs(cpw_Z))
    plt.plot(frequencies, np.abs(meander_Z))

    for cshort in [1e-12, 1e-14, 1e-16, 1e-18, 1e-20]:
    # Cshort = Ccompare # 1e-10
        meander2_Z = get_Z_crossC_meander_res(frequencies * 2 * np.pi, Lcpw, Ccpw, cshort, 20, 10000)
        plt.plot(frequencies, np.abs(meander2_Z), label=cshort)

    plt.legend()
    # plt.plot(frequencies, np.abs(parallel_Z))
    plt.show()
