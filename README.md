# pyspice-lite

A minimal Python API for SPICE circuit simulators (ngspice and compatible).

Define circuits in Python, render SPICE netlists, and run simulations — without the complexity of the original PySpice.

## Requirements

- Python 3.11+
- [ngspice](https://ngspice.sourceforge.io/) installed and on your `PATH` (for simulation)

## Installation

```bash
pip install pyspice-lite
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add pyspice-lite
```

## Quick start

```python
from pyspice_lite import Circuit, Netlist, Simulator

c = (
    Circuit("Voltage Divider")
    .voltage_source("1", "vcc", "0", dc=5.0)
    .resistor("1", "vcc", "mid", 1000.0)
    .resistor("2", "mid", "0", 1000.0)
)

# Render to SPICE netlist
print(Netlist(c).render())

# Run operating point analysis (requires ngspice)
output = Simulator().run(c, ".op")
print(output)
```

Output:

```
Voltage Divider
V1 vcc 0 DC 5.0
R1 vcc mid 1000.0
R2 mid 0 1000.0
.end
```

## Supported elements

| Element | Class | SPICE prefix |
|---|---|---|
| Resistor | `Resistor` | `R` |
| Capacitor | `Capacitor` | `C` |
| Inductor | `Inductor` | `L` |
| Voltage source | `VoltageSource` | `V` |
| Current source | `CurrentSource` | `I` |

## Analysis types

Pass any standard SPICE analysis line to `Simulator.run()`:

```python
sim = Simulator()

sim.run(c, ".op")                        # operating point
sim.run(c, ".tran 1n 1m")               # transient
sim.run(c, ".ac dec 10 1 1Meg")         # AC sweep
```

## Saving netlists

```python
Netlist(c).save("my_circuit.cir")
```

## Custom ngspice path

```python
sim = Simulator(executable="/usr/local/bin/ngspice")
```

## Development

```bash
git clone https://github.com/yourname/pyspice-lite
cd pyspice-lite
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run mypy src/
```

## License

MIT
