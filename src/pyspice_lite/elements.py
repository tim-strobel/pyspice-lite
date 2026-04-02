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


@dataclass
class ModelCard(Element):
    """SPICE .model statement.

    model_type: NPN, PNP, NMOS, PMOS, NJF, PJF, …
    params: optional model parameters, e.g. {"IS": 1e-14, "BF": 100}
    """
    model_type: str
    params: dict[str, float] = field(default_factory=dict)

    def spice_line(self) -> str:
        parts = [f".model {self.name} {self.model_type}"]
        if self.params:
            param_str = " ".join(f"{k}={v}" for k, v in self.params.items())
            parts.append(f"({param_str})")
        return " ".join(parts)


@dataclass
class BJT(Element):
    """Bipolar Junction Transistor.

    SPICE syntax: Qxxx collector base emitter [substrate] model_name [area]
    substrate defaults to '0' when omitted from the netlist line.
    """
    collector: str
    base: str
    emitter: str
    model: str
    substrate: str | None = field(default=None)
    area: float | None = field(default=None)

    def spice_line(self) -> str:
        nodes = [self.collector, self.base, self.emitter]
        if self.substrate is not None:
            nodes.append(self.substrate)
        parts = [f"Q{self.name}"] + nodes + [self.model]
        if self.area is not None:
            parts.append(str(self.area))
        return " ".join(parts)


@dataclass
class JFET(Element):
    """Junction Field-Effect Transistor.

    SPICE syntax: Jxxx drain gate source model_name [area]
    """
    drain: str
    gate: str
    source: str
    model: str
    area: float | None = field(default=None)

    def spice_line(self) -> str:
        parts = [f"J{self.name}", self.drain, self.gate, self.source, self.model]
        if self.area is not None:
            parts.append(str(self.area))
        return " ".join(parts)


@dataclass
class MOSFET(Element):
    """MOSFET transistor.

    SPICE syntax: Mxxx drain gate source bulk model_name [W=val L=val ...]
    """
    drain: str
    gate: str
    source: str
    bulk: str
    model: str
    w: float | None = field(default=None)   # channel width, metres
    l: float | None = field(default=None)   # channel length, metres

    def spice_line(self) -> str:
        parts = [
            f"M{self.name}",
            self.drain, self.gate, self.source, self.bulk,
            self.model,
        ]
        if self.w is not None:
            parts.append(f"W={self.w}")
        if self.l is not None:
            parts.append(f"L={self.l}")
        return " ".join(parts)
