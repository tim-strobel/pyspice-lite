"""Circuit: a collection of elements."""

from .elements import Element


class Circuit:
    def __init__(self, title: str = "pyspice-lite circuit") -> None:
        self.title = title
        self._elements: list[Element] = []

    def add(self, element: Element) -> "Circuit":
        self._elements.append(element)
        return self

    @property
    def elements(self) -> list[Element]:
        return list(self._elements)
