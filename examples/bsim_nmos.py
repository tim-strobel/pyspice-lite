"""
Single NMOS — Id–Vgs transfer characteristic using a BSIM3v3 model.

Two approaches for the model card are shown:

  Option A (production):  use Library() to pull in a foundry PDK file,
                          which already contains the .model statement.

  Option B (shown here):  inline ModelCard with explicit BSIM3v3 parameters,
                          useful for experiments or when no PDK file is at hand.

Circuit
-------
    Vds ──── am(0V) ──── drain
                              │
                            NMOS (BSIM3v3, W=10µm / L=0.18µm)
                              │
    Vgs ─────────── gate    source ─── GND
                              │
                             bulk ─── GND

The zero-volt source "am" acts as an ammeter: I(Vam) = drain current (positive
by SPICE convention when current flows from Vds into the drain).

Analysis
--------
DC sweep of Vgs from 0 V → 1.8 V at a fixed Vds = 0.9 V.
The resulting Id–Vgs curve shows subthreshold slope, Vth, and saturation gm.
"""

from pyspice_lite import (
    Circuit,
    Library,
    ModelCard,
    MOSFET,
    Netlist,
    Simulator,
    VoltageSource,
    plot,
)

# ---------------------------------------------------------------------------
# Process / geometry parameters (180 nm node)
# ---------------------------------------------------------------------------
VDD  = 1.8     # supply voltage, V
VDS  = 0.9     # fixed drain bias (mid-supply), V
W    = 10e-6   # channel width,  m
L    = 0.18e-6 # channel length, m

c = Circuit("BSIM3v3 NMOS Id–Vgs")

# ---------------------------------------------------------------------------
# Model card — choose one of the two options below
# ---------------------------------------------------------------------------

# Option A: include a foundry PDK (comment out Option B to use this)
# c.add(Library("/path/to/foundry.lib", section="tt"))

# Option B: inline BSIM3v3 parameters (180 nm, typical corner)
# U0 is in cm²/(V·s) as required by the BSIM3v3 standard.
c.add(ModelCard("bsim_nmos", model_type="NMOS", params={
    "LEVEL":  8,          # BSIM3v3 in ngspice
    "VERSION": 3.3,
    "TNOM":   27,         # nominal temperature, °C
    # Oxide & geometry
    "TOX":    4.0e-9,     # gate-oxide thickness, m
    "XJ":     1.5e-7,     # junction depth, m
    # Threshold / body effect
    "VTH0":   0.42,       # long-channel Vth at Vbs=0, V
    "K1":     0.60,       # first-order body-effect coefficient, V^0.5
    "K2":    -0.01,       # second-order body-effect coefficient
    # Mobility
    "U0":     300.0,      # low-field mobility, cm²/(V·s)
    "UA":     2.0e-9,     # first-order mobility degradation, m/V
    "UB":     5.0e-19,    # second-order mobility degradation, m²/V²
    # Velocity saturation & CLM
    "VSAT":   8.0e4,      # saturation velocity, m/s
    "PCLM":   1.2,        # channel-length modulation parameter
    # Short-channel effects
    "DVTP0":  1.0e-7,
    "DVTP1":  0.05,
}))

# ---------------------------------------------------------------------------
# Circuit elements
# ---------------------------------------------------------------------------
c.add(VoltageSource("ds", "vds_rail", "0",  dc=VDS))   # drain supply
c.add(VoltageSource("am", "vds_rail", "d",  dc=0.0))   # ammeter (0 V, in series)
c.add(VoltageSource("gs", "g",        "0",  dc=0.0))   # Vgs source (swept)

c.add(MOSFET("n1", drain="d", gate="g", source="0", bulk="0",
             model="bsim_nmos", w=W, l=L))

# ---------------------------------------------------------------------------
# Print netlist
# ---------------------------------------------------------------------------
print("=== Netlist ===")
print(Netlist(c).render())

# ---------------------------------------------------------------------------
# DC sweep: Vgs from 0 V to 1.8 V in 10 mV steps
# I(Vam) = drain current (positive convention via the series ammeter)
# ---------------------------------------------------------------------------
print("\n=== Simulation output ===")
try:
    output = Simulator("/opt/homebrew/bin/ngspice").run(
        c,
        ".dc Vgs 0 1.8 0.01",
        print_vars=["I(Vam)"],
    )
    print(output)
    plot(
        output,
        title="BSIM3v3 NMOS  —  Id vs Vgs  (Vds = 0.9 V)",
        xlabel="Vgs (V)",
        ylabel="Id (A)",
    )
except FileNotFoundError:
    print("ngspice not found — install it to run simulations.")
except Exception as e:
    print(f"Simulation error: {e}")
