"""
RC low-pass filter — transient analysis.

Circuit:
    5V step ── R(1kΩ) ── out ── C(1µF) ── GND

Time constant τ = RC = 1kΩ × 1µF = 1ms
At t=τ, V(out) ≈ 3.16 V (63.2% of 5V)
"""

import sys
import os

from pyspice_lite import Capacitor, Circuit, Netlist, Resistor, Simulator, Transient, VoltageSource

c = Circuit("RC Low-Pass Filter")
c.add(VoltageSource("1", "vin", "0", dc=5.0, waveform="PULSE(0 5 0 1n 1n 10m 20m)"))
c.add(Resistor("1", "vin", "out", 1000.0))
c.add(Capacitor("1", "out", "0", capacitance=1e-6, initial_voltage=0.0))

print("=== Netlist ===")
print(Netlist(c).render())

print("\n=== Simulation output ===")
try:
    output = Simulator("/opt/homebrew/bin/ngspice").run(
        c, Transient(step=1e-4, stop=5e-3, use_initial_conditions=True, print_vars=["V(out)"])
    )
    print(output)
except FileNotFoundError:
    print("ngspice not found — install it to run simulations.")
except Exception as e:
    print(f"Simulation error: {e}")
