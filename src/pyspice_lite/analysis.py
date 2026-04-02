"""Analysis types: structured representations of SPICE analysis commands."""

from dataclasses import dataclass, field


@dataclass
class Analysis:
    print_vars: list[str] = field(default_factory=list)

    @property
    def spice_type(self) -> str:
        raise NotImplementedError

    def spice_line(self) -> str:
        raise NotImplementedError

    def print_line(self) -> str | None:
        if not self.print_vars:
            return None
        return f".print {self.spice_type} {' '.join(self.print_vars)}"


@dataclass
class OP(Analysis):
    """DC operating point analysis."""

    @property
    def spice_type(self) -> str:
        return "op"

    def spice_line(self) -> str:
        return ".op"


@dataclass
class Transient(Analysis):
    """
    Transient analysis.

    Parameters
    ----------
    step:
        Time step (seconds), e.g. 1e-4.
    stop:
        Stop time (seconds), e.g. 5e-3.
    start:
        Start time (seconds, default 0).
    use_initial_conditions:
        If True, appends `uic` — ngspice skips the DC OP and honours IC= values.
    """

    step: float = 0.0
    stop: float = 0.0
    start: float = 0.0
    use_initial_conditions: bool = False

    @property
    def spice_type(self) -> str:
        return "tran"

    def spice_line(self) -> str:
        parts = [".tran", _eng(self.step), _eng(self.stop)]
        if self.start:
            parts.append(_eng(self.start))
        if self.use_initial_conditions:
            parts.append("uic")
        return " ".join(parts)


@dataclass
class AC(Analysis):
    """
    AC small-signal frequency sweep.

    Parameters
    ----------
    variation:
        Sweep type: "dec" (decade), "oct" (octave), or "lin" (linear).
    points:
        Number of points per interval.
    start_freq:
        Start frequency in Hz.
    stop_freq:
        Stop frequency in Hz.
    """

    variation: str = "dec"
    points: int = 10
    start_freq: float = 1.0
    stop_freq: float = 1e6

    @property
    def spice_type(self) -> str:
        return "ac"

    def spice_line(self) -> str:
        return f".ac {self.variation} {self.points} {_eng(self.start_freq)} {_eng(self.stop_freq)}"


@dataclass
class DC(Analysis):
    """
    DC sweep analysis.

    Parameters
    ----------
    source:
        Name of the source to sweep, e.g. "V1".
    start:
        Start value.
    stop:
        Stop value.
    step:
        Step size.
    """

    source: str = ""
    start: float = 0.0
    stop: float = 0.0
    step: float = 0.0

    @property
    def spice_type(self) -> str:
        return "dc"

    def spice_line(self) -> str:
        return f".dc {self.source} {self.start} {self.stop} {self.step}"


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _eng(value: float) -> str:
    """Format a float without trailing zeros, keeping scientific notation compact."""
    return f"{value:g}"
