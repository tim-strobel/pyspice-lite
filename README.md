# pyspice-lite

A minimal Python API for SPICE circuit simulators (ngspice and compatible).

Define circuits in Python, render SPICE netlists, and run simulations — without the complexity of the original PySpice.

## Requirements

- Python 3.11+
- [ngspice](https://ngspice.sourceforge.io/) installed and on your `PATH` (for simulation)
- [matplotlib](https://matplotlib.org/) (optional, for plotting)

## Quick start

```python
from pyspice_lite import Circuit, Netlist, OP, Resistor, Simulator, VoltageSource

c = Circuit("Voltage Divider")
c.add(VoltageSource("1", "vcc", "0", dc=5.0))
c.add(Resistor("1", "vcc", "mid", 1000.0))
c.add(Resistor("2", "mid", "0", 1000.0))

# Render to SPICE netlist
print(Netlist(c).render())

# Run operating point analysis (requires ngspice)
output = Simulator().run(c, OP(print_vars=["V(mid)", "V(vcc)"]))
print(output)
```

Netlist output:

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
| BJT | `BJT` | `Q` |
| JFET | `JFET` | `J` |
| MOSFET | `MOSFET` | `M` |
| Model card | `ModelCard` | `.model` |
| Library include | `Library` | `.lib` |

### Capacitor / Inductor initial conditions

```python
from pyspice_lite import Capacitor, Inductor

Capacitor("1", "a", "b", capacitance=1e-6, initial_voltage=3.3)
Inductor("1", "a", "b", inductance=1e-3, initial_current=0.01)
```

### Transistors

```python
from pyspice_lite import BJT, JFET, MOSFET, ModelCard

# BJT
ModelCard("2N2222", model_type="NPN", params={"IS": 1e-14, "BF": 100})
BJT("1", collector="out", base="in", emitter="0", model="2N2222")

# JFET
ModelCard("J2N5457", model_type="NJF")
JFET("1", drain="out", gate="in", source="0", model="J2N5457")

# MOSFET (W and L in metres)
ModelCard("NMOS1", model_type="NMOS")
MOSFET("1", drain="d", gate="g", source="s", bulk="0", model="NMOS1", w=10e-6, l=1e-6)
```

### External model libraries

```python
from pyspice_lite import Library

c.add(Library("/path/to/pdk.lib", section="tt"))
```

### Waveform sources

```python
VoltageSource("1", "vin", "0", ac=1.0, waveform="SIN(0 1 1k)")
```

## Analysis types

Pass an `Analysis` object or a raw SPICE string to `Simulator.run()`.

### Structured API

```python
from pyspice_lite import AC, DC, OP, Transient, Simulator

sim = Simulator()

# Operating point
sim.run(c, OP())

# Transient
sim.run(c, Transient(step=1e-6, stop=1e-3))

# AC sweep (decade, 10 pts/decade, 1 Hz – 1 MHz)
sim.run(c, AC(variation="dec", points=10, start_freq=1, stop_freq=1e6))

# DC sweep
sim.run(c, DC(source="V1", start=0, stop=5, step=0.1))
```

Attach print variables directly on the analysis object:

```python
output = sim.run(c, AC(variation="dec", points=10, start_freq=1, stop_freq=100e3,
                        print_vars=["V(out)"]))
```

### Raw SPICE strings

```python
sim.run(c, ".op")
sim.run(c, ".tran 1n 1m", print_vars=["V(out)"])
sim.run(c, ".ac dec 10 1 1Meg")
```

## Plotting

`plot()` parses ngspice `.print` output and renders it with matplotlib. The x-axis scale defaults to log for frequency sweeps.

```python
from pyspice_lite import plot

output = Simulator().run(c, AC(..., print_vars=["V(out)"]))
fig, ax = plot(output, title="RC low-pass", ylabel="Amplitude (V)")
```

Parameters:

| Parameter | Default | Description |
|---|---|---|
| `title` | `""` | Figure title |
| `xlabel` | *(x-column name)* | X-axis label |
| `ylabel` | `""` | Y-axis label |
| `xscale` | `"linear"` (`"log"` for freq) | `"linear"` or `"log"` |
| `yscale` | `"linear"` | `"linear"` or `"log"` |
| `show` | `True` | Call `plt.show()` automatically |

Parse the table without plotting:

```python
from pyspice_lite import parse_print_output

data = parse_print_output(output)   # dict[str, list[float]]
```

## Saving netlists

```python
Netlist(c).save("my_circuit.cir")
```

## Custom ngspice path

```python
sim = Simulator(executable="/usr/local/bin/ngspice")
```

## Examples

| File | Description |
|---|---|
| [examples/voltage_divider.py](examples/voltage_divider.py) | Resistor voltage divider, operating point |
| [examples/ac_sweep.py](examples/ac_sweep.py) | RC low-pass filter, AC frequency sweep |
| [examples/rc_transient.py](examples/rc_transient.py) | RC low-pass filter, transient step response |
| [examples/ring_oscillator.py](examples/ring_oscillator.py) | 3-stage CMOS ring oscillator, transient analysis |
| [examples/bsim_nmos.py](examples/bsim_nmos.py) | Single NMOS Id–Vgs sweep with BSIM3v3 model card |

## Development

```bash
git clone https://github.com/yourname/pyspice-lite
cd pyspice-lite
python -m venv venv
source venv/bin/activate
pip install -e .
```

## License

MIT
