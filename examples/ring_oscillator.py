"""
3-stage CMOS ring oscillator — transient analysis.

Each stage is a CMOS inverter (PMOS pull-up + NMOS pull-down).
An odd number of inverters wired in a ring produces self-sustaining
oscillation.

Ring connections (node names encode the wiring):
    n1 → stage1 → n2 → stage2 → n3 → stage3 → n1  (ring closure)

A 1 ns kick pulse on n1 breaks symmetry so the simulation starts
oscillating instead of sitting at the meta-stable mid-point.

Topology per stage (stage drives node out from node inp):
    VDD ──┬── PMOS(gate=inp, source=VDD, drain=out, bulk=VDD)
          └── NMOS(gate=inp, source=GND, drain=out, bulk=GND)
"""

from pyspice_lite import (
    Circuit,
    ModelCard,
    MOSFET,
    Netlist,
    Resistor,
    Simulator,
    Transient,
    VoltageSource,
    plot,
)

VDD = 3.3      # supply voltage, V
W_N = 2e-6     # NMOS channel width, m
W_P = 4e-6     # PMOS channel width (2× for symmetric drive strength), m
L   = 0.5e-6   # channel length, m
N_STAGES = 3   # must be odd

# 1. Create circuit and supply
c = Circuit(f"{N_STAGES}-Stage CMOS Ring Oscillator")
c.add(VoltageSource("dd", "vdd", "0", dc=VDD))

# 2. Define MOSFET models (level-1, simplified)
c.add(ModelCard("NMOS1", model_type="NMOS", params={
    "LEVEL": 1, "VTO": 0.5,  "KP": 120e-6, "LAMBDA": 0.01,
    "TOX": 10e-9, "GAMMA": 0.4, "PHI": 0.65,
}))
c.add(ModelCard("PMOS1", model_type="PMOS", params={
    "LEVEL": 1, "VTO": -0.5, "KP":  60e-6, "LAMBDA": 0.01,
    "TOX": 10e-9, "GAMMA": 0.4, "PHI": 0.65,
}))

# 3. Wire inverter stages into a ring
# n{i} is the input of stage i and the output of stage i-1.
# The last stage drives n1, closing the loop.
nodes = [f"n{i + 1}" for i in range(N_STAGES)]
for i in range(N_STAGES):
    inp = nodes[i]
    out = nodes[(i + 1) % N_STAGES]
    c.add(MOSFET(f"p{i+1}", drain=out, gate=inp, source="vdd", bulk="vdd",
                 model="PMOS1", w=W_P, l=L))
    c.add(MOSFET(f"n{i+1}", drain=out, gate=inp, source="0",   bulk="0",
                 model="NMOS1", w=W_N, l=L))

# 4. Add kick pulse on n1 to break symmetry (1 GΩ series resistor keeps it passive in steady state)
c.add(VoltageSource("kick", "kick_src", "0", waveform="PULSE(3.3 0 0 1p 1p 1n 1000)"))
c.add(Resistor("kick", "kick_src", "n1", 1e9))

# 5. Render netlist
print(Netlist(c).render())

# 6. Run transient simulation
try:
    analysis = Transient(
        step=10e-12,
        stop=10e-9,
        print_vars=[f"V(n{i+1})" for i in range(N_STAGES)],
    )
    output = Simulator("/opt/homebrew/bin/ngspice").run(c, analysis)
    print(output)
    plot(output, title=f"{N_STAGES}-Stage CMOS Ring Oscillator", ylabel="Voltage (V)")
except FileNotFoundError:
    print("ngspice not found — install it to run simulations.")
except Exception as e:
    print(f"Simulation error: {e}")
