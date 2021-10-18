import numpy as np
import matplotlib.pyplot as plt
from snail_solver.ancilla import Ancilla
from snail_solver.helper_functions import *
from snail_solver.snail_element import SNAIL

fock_trunc = 30

# Create SNAIL
snail_parameters = {"n": 3, "alpha": 0.320, "phi_ext": 0.470 * 2 * np.pi}
Lj = 11.0e-9
freq = 5.19381e9

snail = SNAIL.from_Lj(Lj, snail_parameters)
ancilla = Ancilla(snail, freq, fock_trunc=fock_trunc)

# get qutip hamiltonian operator
evals, evecs = ancilla.calculate_spectrum()
evals, evecs = clean_spectrum(evals, evecs)  # Remove weird states

fig, axes = plt.subplots(2, 1, sharex=True)
add_transition_energies_plot(axes[0], evals)
add_anharmonicity_plot(axes[1], evals)
plt.show()