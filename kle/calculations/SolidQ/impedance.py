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

    # print("Cl, Cm:", Cl, Cm)

    seg_imp_to_gnd0 = get_segment_imp_to_gnd(omega, 0, Cc, Cm, Cl)
    seg_imp_to_gnd1 = get_segment_imp_to_gnd(omega, m-1, Cc, Cm, Cl)
    
    imp_to_gnd = (1.j * omega * Cm + 1/seg_imp_to_gnd0 + 1/seg_imp_to_gnd1)**-1
    
    for j in range(m):
        seg_imp_to_gnd0 = get_segment_imp_to_gnd(omega, j, Cc, Cm, Cl)
        seg_imp_to_gnd1 = get_segment_imp_to_gnd(omega, m-j-1, Cc, Cm, Cl)
        # print("Ceff, j:", (1.j * omega * Cm + 1/seg_imp_to_gnd0 + 1/seg_imp_to_gnd1)[0]/(1.j * omega[0]))
        for i in range(n//m):
            imp_to_gnd = imp_to_gnd + 1.j * omega * Ll
            imp_to_gnd = (1/imp_to_gnd + (1.j * omega * Cm) + 1/seg_imp_to_gnd0 + 1/seg_imp_to_gnd1)**-1

    return imp_to_gnd

if __name__ == "__main__":
    # frequencies = np.linspace(1e9, 20e9, 5000)
    frequencies = np.linspace(8e9, 12e9, 5000)

    Z0 = 5000
    L = 26.5e-9 * 5
    C = L/(Z0**2)
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

    def f_fit(omega, L, C):
        return 1/np.abs(omega * L / (1 - L * C * omega**2))
    
    import scipy.optimize as opt
    
    # plt.plot(frequencies, f_fit(frequencies * 2 * np.pi, L, C), label=f"fit0", ls="-")

    p0 = [6e-8, 1.17e-14/3]
    plt.plot(frequencies, 1/f_fit(frequencies * 2 * np.pi, *p0), label=f"fit0", ls="-")

    Ccross = 1e-18
    for M in [15,]:
        Z_LC = get_Z_meander(frequencies * 2 * np.pi, L * np.pi, C * np.pi, Ccross, 5000, M)
        
        res, _ = opt.curve_fit(f_fit, frequencies * 2 * np.pi, 1/np.abs(Z_LC), p0=p0)
        # plt.plot(frequencies, f_fit(frequencies * 2 * np.pi, *[L, C/(64/36)]), label=f"fit0, {M}", ls="-")
        
        print(res, (res[0]/res[1])**0.5)
        
        
        plt.plot(frequencies, np.abs(Z_LC), label=f"meander Ccomplex, {M}", ls="--")
        plt.plot(frequencies, 1/f_fit(frequencies * 2 * np.pi, *res), label=f"fit, {M}", ls="-")


    plt.legend()
    plt.show()

