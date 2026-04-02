"""
Voltage divider — operating point analysis.

Circuit:
    5V ── R1(1kΩ) ── mid ── R2(1kΩ) ── GND

Expected: V(mid) = 2.5 V
"""

import sys
import os

from pyspice_lite import Circuit, Netlist, OP, Resistor, Simulator, VoltageSource

c = Circuit("Voltage Divider")
c.add(VoltageSource("1", "vcc", "0", dc=5.0))
c.add(Resistor("1", "vcc", "mid", 1000.0))
c.add(Resistor("2", "mid", "0", 1000.0))

print("=== Netlist ===")
print(Netlist(c).render())

print("\n=== Simulation output ===")
try:
    output = Simulator("/opt/homebrew/bin/ngspice").run(c, OP(print_vars=["V(mid)", "V(vcc)"]))
    print(output)
except FileNotFoundError:
    print("ngspice not found — install it to run simulations.")
except Exception as e:
    print(f"Simulation error: {e}")
