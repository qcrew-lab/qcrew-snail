import os
import numpy as np
import matplotlib.pyplot as plt
from snail_solver.snail_element import SNAIL
from snail_solver.ancilla import Ancilla
from snail_solver.circuit import Circuit
from snail_solver.helper_functions import *
from snail_solver.epr_analysis import epr_analysis, get_epr_circuit_params

# Executes EPR analysis
HFSS_project_path = os.getcwd()
HFSS_project_name = "SNAIL_test"
junction_info = [
    (
        "j1",  # assign junction name
        {
            "Lj_variable": "junction_LJ",
            "rect": "junction_left",
            "line": "junction_line",
            "length": "junction_l",
            "Cj_variable": "junction_CJ",
        },  # related HFSS variable names
    )
]
_ = epr_analysis(HFSS_project_path, HFSS_project_name, junction_info)
# Obtain circuit parameters from pyEPR
variation = 0
epr_Lj, epr_freqs, epr_phi_rzpf = get_epr_circuit_params(*_, variation)

# Define fixed circuit parameters
fock_trunc = 18
n = 3
Lj = epr_Lj
freqs = epr_freqs
phi_rzpf = epr_phi_rzpf

# Sweep SNAIL parameters alpha and phi_ext
cavity_kerr_list = []
max_kerr_list = []
alpha_list = np.arange(0.2, 0.4, 0.01)
phi_ext_list = np.arange(0.2 * 2 * np.pi, 0.491 * 2 * np.pi, 0.01 * 2 * np.pi)
for alpha in alpha_list:
    for phi_ext in phi_ext_list:

        # assemble circuit
        snail = SNAIL.from_Lj(Lj, n, alpha, phi_ext)
        ancilla = Ancilla(snail, freqs[np.argmax(phi_rzpf)], fock_trunc=fock_trunc)
        circuit = Circuit(ancilla, freqs, phi_rzpf)

        # diagonalize coupled hamiltonian
        evals, evecs = circuit.circuit_spectrum

        cavity_evals = [
            circuit.get_eigenstate({1: i})[0] for i in range(fock_trunc - 3)
        ]

        # Calculate optimization variables
        relative_evals = np.real(cavity_evals - cavity_evals[0])
        transit_energies = relative_evals[1:] - relative_evals[:-1]
        anharm = transit_energies[1:] - transit_energies[:-1]
        avg_kerr = np.average(anharm)
        max_kerr = np.max(np.abs(anharm))

        # Save for plotting
        cavity_kerr_list.append(avg_kerr)
        max_kerr_list.append(max_kerr)

# Adjust and reshape values for colormesh plotting
phi_ext_list /= 2 * np.pi  # plot in units of 2pi
reshape_dim = (len(alpha_list), len(phi_ext_list))
cavity_kerr_list = np.reshape(cavity_kerr_list, reshape_dim)
max_kerr_list = np.reshape(max_kerr_list, reshape_dim)

# Plot
fig, axes = plt.subplots(1, 2, sharey=True, sharex=True)

im1 = axes[0].pcolormesh(
    phi_ext_list, alpha_list, cavity_kerr_list, shading="auto", cmap="bwr"
)
im1.set_clim(-0.6, 0.6)
fig.colorbar(im1, ax=axes[0])
axes[0].set_title("Average cavity Kerr")
axes[0].set_ylabel("Josephson energy proportion alpha")
axes[0].set_xlabel("External flux (per flux quanta)")

im2 = axes[1].pcolormesh(
    phi_ext_list, alpha_list, max_kerr_list, shading="auto", cmap="bwr"
)
im2.set_clim(0, 0.6)
fig.colorbar(im2, ax=axes[1])
axes[1].set_title("Maximum absolute cavity Kerr")
axes[1].set_xlabel("External flux (per flux quanta)")

plt.show()