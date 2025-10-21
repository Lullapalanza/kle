import numpy as np
import matplotlib.pyplot as plt

def get_Z_LC(omega, L, C):
    return (1/(omega * 1.j * L) + omega * 1.j * C)**-1

def get_Z_CPW(omega, L, C, n):
    Ll, Cl = L/n, C/n

    imp_to_gnd = 1/(1.j * omega * Cl)
    for i in range(n):
        imp_to_gnd = imp_to_gnd + 1.j * omega * Ll
        imp_to_gnd = (1/imp_to_gnd + 1.j * omega * Cl)**-1

    return imp_to_gnd

def get_Z_shuntC_CPW(omega, L, C, Cshunt, n):
    Ll, Cl = L/n, C/n

    imp_to_gnd = 1/(1.j * omega * Cl)
    for i in range(n):
        imp_to_gnd = imp_to_gnd + (1/(1.j * omega * Ll) + 1.j * omega * Cshunt)**-1
        imp_to_gnd = (1/imp_to_gnd + 1.j * omega * Cl)**-1

    return imp_to_gnd

def get_segment_imp_to_gnd(omega, n, Cc, Cg, Cgl):
    imp_to_gnd = 2/(1.j * omega * Cgl) + 1/(1.j * omega * Cc)
    # imp_to_gnd = 1/(1.j * omega * Cg) + 1/(1.j * omega * Cc)
#     print(
#         (1/imp_to_gnd[0])/omega[0]
#     )
    for i in range(1, n):
        imp_to_gnd = (1/imp_to_gnd + 1.j * omega * Cg)**-1 + 1/(1.j * omega * Cc)
    return imp_to_gnd

def get_Z_meander(omega, L, C, Cc, n, m):
    Ll, Cl = L/n, C/n
    Cm = Cl/m

    print("Cl, Cm:", Cl, Cm)

    seg_imp_to_gnd0 = get_segment_imp_to_gnd(omega, 0, Cc, Cm, Cl)
    seg_imp_to_gnd1 = get_segment_imp_to_gnd(omega, m-1, Cc, Cm, Cl)
    
    imp_to_gnd = (1.j * omega * Cm + 1/seg_imp_to_gnd0 + 1/seg_imp_to_gnd1)**-1
    
    for j in range(m):
        seg_imp_to_gnd0 = get_segment_imp_to_gnd(omega, j, Cc, Cm, Cl)
        seg_imp_to_gnd1 = get_segment_imp_to_gnd(omega, m-j-1, Cc, Cm, Cl)
        print("Ceff, j:", (1.j * omega * Cm + 1/seg_imp_to_gnd0 + 1/seg_imp_to_gnd1)[0]/(1.j * omega[0]))
        for i in range(n//m):
            imp_to_gnd = imp_to_gnd + 1.j * omega * Ll
            imp_to_gnd = (1/imp_to_gnd + (1.j * omega * Cm) + 1/seg_imp_to_gnd0 + 1/seg_imp_to_gnd1)**-1

    return imp_to_gnd

if __name__ == "__main__":
    frequencies = np.linspace(1e9, 20e9, 10000)

    L = 26.5e-9
    C = L/1e6
    Z_LC = get_Z_LC(frequencies * 2 * np.pi, L, C)
    print("LC f (GHz), Z", 1e-9/(2*np.pi * (L*C)**0.5), (L/C)**0.5)
    # plt.plot(frequencies, np.abs(Z_LC), label="lumped")

    Z_LC = get_Z_CPW(frequencies * 2 * np.pi, L * np.pi, C * np.pi, 5000)
    plt.plot(frequencies, np.abs(Z_LC), label="CPW")

    # for Ccross in [1e-13, 1e-14, 1e-15, 1.66504e-16, 1e-17, 1e-20, 1e-30]:
    #     Z_LC = get_Z_shuntC_CPW(frequencies * 2 * np.pi, L * np.pi, C * np.pi, Ccross, 5000)
    #     plt.plot(frequencies, np.abs(Z_LC), label=f"meander Cshunt, {Ccross}")


    # for Ccross in [1e-11, 1e-14, 1e-17, 0.5e-18]:
    #     Z_LC = get_Z_meander(frequencies * 2 * np.pi, L * np.pi, C * np.pi, Ccross, 5000, 20)
    #     plt.plot(frequencies, np.abs(Z_LC), label=f"meander Ccomplex, {Ccross}")

    Ccross = 1e-17
    for M in [10, 15, 20, 25, 30, 35, 45, 70, 100]:
        Z_LC = get_Z_meander(frequencies * 2 * np.pi, L * np.pi, C * np.pi, Ccross, 5000, M)
        plt.plot(frequencies, np.abs(Z_LC), label=f"meander Ccomplex, {M}")

    plt.legend()
    plt.show()

