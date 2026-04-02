"""
RC low-pass filter — AC frequency sweep.

Circuit:
    Vac ── R(1kΩ) ── out ── C(1µF) ── GND

Corner frequency f_c = 1 / (2π·RC) ≈ 159 Hz
"""

import sys
import os

from pyspice_lite import AC, Capacitor, Circuit, Netlist, Resistor, Simulator, VoltageSource

c = Circuit("RC AC Sweep")
c.add(VoltageSource("1", "vin", "0", ac=1.0))
c.add(Resistor("1", "vin", "out", 1000.0))
c.add(Capacitor("1", "out", "0", capacitance=1e-6))

print("=== Netlist ===")
print(Netlist(c).render())

print("\n=== Simulation output ===")
try:
    # Decade sweep: 10 points/decade from 1 Hz to 100 kHz
    output = Simulator("/opt/homebrew/bin/ngspice").run(
        c, AC(variation="dec", points=10, start_freq=1, stop_freq=100e3, print_vars=["V(out)"])
    )
    print(output)
except FileNotFoundError:
    print("ngspice not found — install it to run simulations.")
except Exception as e:
    print(f"Simulation error: {e}")
