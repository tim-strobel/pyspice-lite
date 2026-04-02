"""Simulator: runs ngspice (or compatible) on a Circuit and returns raw output."""

import subprocess
import tempfile
from pathlib import Path

from .analysis import Analysis
from .circuit import Circuit
from .netlist import Netlist


class SimulatorError(Exception):
    pass


class Simulator:
    def __init__(self, executable: str = "ngspice") -> None:
        self.executable = executable

    def run(self, circuit: Circuit, analysis: Analysis | str, print_vars: list[str] | None = None) -> str:
        """
        Run a simulation and return raw ngspice stdout.

        Parameters
        ----------
        circuit:
            The circuit to simulate.
        analysis:
            An Analysis object (OP, Transient, AC, DC) or a raw SPICE string.
        print_vars:
            Override print variables. When using an Analysis object, prefer
            setting print_vars on the object itself instead.
        """
        netlist = Netlist(circuit)
        raw = netlist.render()

        if isinstance(analysis, Analysis):
            analysis_line = analysis.spice_line()
            resolved_print = analysis.print_line() or (
                f".print {analysis.spice_type} {' '.join(print_vars)}" if print_vars else None
            )
        else:
            analysis_type = analysis.strip().split()[0].lstrip(".")
            analysis_line = analysis
            resolved_print = (
                f".print {analysis_type} {' '.join(print_vars)}" if print_vars else None
            )

        extra = analysis_line
        if resolved_print:
            extra += f"\n{resolved_print}"

        raw = raw.replace(".end", extra + "\n.end")

        with tempfile.TemporaryDirectory() as tmpdir:
            netlist_path = Path(tmpdir) / "circuit.cir"
            netlist_path.write_text(raw)

            result = subprocess.run(
                [self.executable, "-b", str(netlist_path)],
                capture_output=True,
                text=True,
            )

        if result.returncode != 0:
            raise SimulatorError(result.stderr or result.stdout)

        return result.stdout
