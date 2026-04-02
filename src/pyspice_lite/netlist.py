"""Netlist: renders a Circuit to a SPICE netlist string."""

from .circuit import Circuit


class Netlist:
    def __init__(self, circuit: Circuit) -> None:
        self.circuit = circuit

    def render(self) -> str:
        lines = [self.circuit.title]
        for element in self.circuit.elements:
            lines.append(element.spice_line())
        lines.append(".end")
        return "\n".join(lines)

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.render())
