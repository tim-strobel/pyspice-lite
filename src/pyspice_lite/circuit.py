"""Circuit: a collection of elements."""

from .elements import SpiceElement


class Circuit:
    def __init__(self, title: str = "pyspice-lite circuit") -> None:
        self.title = title
        self._elements: list[SpiceElement] = []

    def add(self, element: SpiceElement) -> "Circuit":
        self._elements.append(element)
        return self

    @property
    def elements(self) -> list[SpiceElement]:
        return list(self._elements)
