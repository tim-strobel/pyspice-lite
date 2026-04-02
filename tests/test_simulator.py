"""Integration tests that run ngspice. Requires ngspice at NGSPICE_PATH."""

import math
import os
import pytest

from pyspice_lite import Capacitor, Circuit, Resistor, Simulator, VoltageSource
from pyspice_lite.simulator import SimulatorError

NGSPICE = os.environ.get("NGSPICE_PATH", "/opt/homebrew/bin/ngspice")

pytestmark = pytest.mark.skipif(
    not os.path.isfile(NGSPICE),
    reason=f"ngspice not found at {NGSPICE}",
)


def sim() -> Simulator:
    return Simulator(NGSPICE)


# ---------------------------------------------------------------------------
# Output parsing helpers
# ---------------------------------------------------------------------------

def _parse_table(output: str) -> list[dict[str, float]]:
    """
    Parse the ngspice .print table from batch output.

    Returns a list of dicts: [{"index": 0, "v(mid)": 2.5, ...}, ...]
    For AC analysis, complex columns (real, imag) are returned as magnitude.
    Complex values are identified by a trailing comma on the real token.
    """
    rows = []
    lines = output.splitlines()

    header_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("Index") and i + 1 < len(lines) and lines[i + 1].strip().startswith("---"):
            header_idx = i
            break

    if header_idx is None:
        return rows

    headers = lines[header_idx].split()
    data_start = header_idx + 2

    for line in lines[data_start:]:
        line = line.strip()
        if not line or line.startswith("---") or line.startswith("Index"):
            continue
        if line.startswith("Total"):
            break
        tokens = line.split()
        row: dict[str, float] = {}
        t = 0
        for header in headers:
            if t >= len(tokens):
                break
            token = tokens[t]
            t += 1
            if token.endswith(",") and t < len(tokens):
                real = float(token.rstrip(","))
                imag = float(tokens[t])
                t += 1
                row[header.lower()] = math.sqrt(real**2 + imag**2)
            else:
                row[header.lower()] = float(token)
        rows.append(row)

    return rows


# ---------------------------------------------------------------------------
# Operating point
# ---------------------------------------------------------------------------

class TestOperatingPoint:
    def test_voltage_divider_midpoint(self):
        """V(mid) must be exactly half of supply (2.5 V)."""
        c = Circuit("Voltage Divider")
        c.add(VoltageSource("1", "vcc", "0", dc=5.0))
        c.add(Resistor("1", "vcc", "mid", 1000.0))
        c.add(Resistor("2", "mid", "0", 1000.0))

        output = sim().run(c, ".op", print_vars=["V(mid)", "V(vcc)"])
        rows = _parse_table(output)

        assert len(rows) == 1
        assert rows[0]["v(mid)"] == pytest.approx(2.5, rel=1e-4)
        assert rows[0]["v(vcc)"] == pytest.approx(5.0, rel=1e-4)

    def test_asymmetric_divider(self):
        """V(mid) = Vcc * R2 / (R1 + R2) = 5 * 2k / 3k = 3.333 V."""
        c = Circuit("Asymmetric Divider")
        c.add(VoltageSource("1", "vcc", "0", dc=5.0))
        c.add(Resistor("1", "vcc", "mid", 1000.0))
        c.add(Resistor("2", "mid", "0", 2000.0))

        output = sim().run(c, ".op", print_vars=["V(mid)"])
        rows = _parse_table(output)

        assert rows[0]["v(mid)"] == pytest.approx(10 / 3, rel=1e-4)


# ---------------------------------------------------------------------------
# AC analysis
# ---------------------------------------------------------------------------

class TestACSweep:
    def _rc_circuit(self) -> Circuit:
        # Corner freq f_c = 1 / (2π·RC) = 1 / (2π·1k·1µ) ≈ 159.15 Hz
        c = Circuit("RC Low-Pass")
        c.add(VoltageSource("1", "vin", "0", ac=1.0))
        c.add(Resistor("1", "vin", "out", 1000.0))
        c.add(Capacitor("1", "out", "0", capacitance=1e-6))
        return c

    def test_passband_gain_near_unity(self):
        """At 1 Hz (well below f_c), |V(out)| ≈ 1.0."""
        output = sim().run(self._rc_circuit(), ".ac lin 1 1 1", print_vars=["V(out)"])
        rows = _parse_table(output)
        assert rows[0]["v(out)"] == pytest.approx(1.0, rel=1e-3)

    def test_corner_frequency_gain(self):
        """|V(out)| at f_c ≈ 159 Hz must be 1/√2 ≈ 0.7071 (−3 dB point)."""
        output = sim().run(self._rc_circuit(), ".ac lin 1 159.15 159.15", print_vars=["V(out)"])
        rows = _parse_table(output)
        assert rows[0]["v(out)"] == pytest.approx(1 / math.sqrt(2), rel=1e-2)

    def test_stopband_attenuation(self):
        """At 100 kHz (well above f_c), |V(out)| must be < 0.01."""
        output = sim().run(self._rc_circuit(), ".ac lin 1 100000 100000", print_vars=["V(out)"])
        rows = _parse_table(output)
        assert rows[0]["v(out)"] < 0.01


# ---------------------------------------------------------------------------
# Transient analysis
# ---------------------------------------------------------------------------

class TestTransient:
    def test_rc_charging_reaches_steady_state(self):
        """
        RC charging from IC=0: after 10τ (τ=1ms → t=10ms), V(out) ≈ 5V.
        Uses `uic` so ngspice honours IC=0 instead of running a DC OP first.
        """
        c = Circuit("RC Charging")
        c.add(VoltageSource("1", "vin", "0", dc=5.0))
        c.add(Resistor("1", "vin", "out", 1000.0))
        c.add(Capacitor("1", "out", "0", capacitance=1e-6, initial_voltage=0.0))

        output = sim().run(c, ".tran 0.1m 10m uic", print_vars=["V(out)"])
        rows = _parse_table(output)

        assert rows[-1]["v(out)"] == pytest.approx(5.0, rel=1e-2)

    def test_rc_initial_voltage_is_zero(self):
        """V(out) at t=0 must start from IC=0."""
        c = Circuit("RC Charging")
        c.add(VoltageSource("1", "vin", "0", dc=5.0, waveform="PULSE(0 5 0 1n 1n 100m 200m)"))
        c.add(Resistor("1", "vin", "out", 1000.0))
        c.add(Capacitor("1", "out", "0", capacitance=1e-6, initial_voltage=0.0))

        output = sim().run(c, ".tran 0.1m 10m uic", print_vars=["V(out)"])
        rows = _parse_table(output)

        assert rows[0]["v(out)"] == pytest.approx(0.0, abs=0.1)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrors:
    def test_invalid_executable_raises(self):
        c = Circuit("X")
        c.add(VoltageSource("1", "a", "0", dc=1.0))
        with pytest.raises(FileNotFoundError):
            Simulator("/nonexistent/ngspice").run(c, ".op")
