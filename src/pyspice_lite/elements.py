"""SPICE circuit element definitions."""

from dataclasses import dataclass, field


@dataclass
class Element:
    name: str

    def spice_line(self) -> str:
        raise NotImplementedError


@dataclass
class Resistor(Element):
    n1: str
    n2: str
    resistance: float  # Ohms

    def spice_line(self) -> str:
        return f"R{self.name} {self.n1} {self.n2} {self.resistance}"


@dataclass
class Capacitor(Element):
    n1: str
    n2: str
    capacitance: float  # Farads
    initial_voltage: float | None = field(default=None)

    def spice_line(self) -> str:
        line = f"C{self.name} {self.n1} {self.n2} {self.capacitance}"
        if self.initial_voltage is not None:
            line += f" IC={self.initial_voltage}"
        return line


@dataclass
class Inductor(Element):
    n1: str
    n2: str
    inductance: float  # Henrys
    initial_current: float | None = field(default=None)

    def spice_line(self) -> str:
        line = f"L{self.name} {self.n1} {self.n2} {self.inductance}"
        if self.initial_current is not None:
            line += f" IC={self.initial_current}"
        return line


@dataclass
class VoltageSource(Element):
    n1: str
    n2: str
    dc: float | None = field(default=None)      # V
    ac: float | None = field(default=None)      # V amplitude
    waveform: str | None = field(default=None)  # e.g. "SIN(0 1 1k)"

    def spice_line(self) -> str:
        parts = [f"V{self.name}", self.n1, self.n2]
        if self.dc is not None:
            parts.append(f"DC {self.dc}")
        if self.ac is not None:
            parts.append(f"AC {self.ac}")
        if self.waveform is not None:
            parts.append(self.waveform)
        return " ".join(parts)


@dataclass
class CurrentSource(Element):
    n1: str
    n2: str
    dc: float | None = field(default=None)      # A
    ac: float | None = field(default=None)      # A amplitude
    waveform: str | None = field(default=None)

    def spice_line(self) -> str:
        parts = [f"I{self.name}", self.n1, self.n2]
        if self.dc is not None:
            parts.append(f"DC {self.dc}")
        if self.ac is not None:
            parts.append(f"AC {self.ac}")
        if self.waveform is not None:
            parts.append(self.waveform)
        return " ".join(parts)
