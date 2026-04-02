"""Plotting helpers: parse ngspice batch output and render with matplotlib."""

import re
from typing import Optional


def parse_print_output(output: str) -> dict[str, list[float]]:
    """
    Parse the table produced by ngspice's ``.print`` command.

    Returns a dict mapping each column header to a list of float values.
    The first data column is usually ``time``, ``frequency``, or the swept
    source name; the remaining columns are the requested signals.

    Raises ``ValueError`` if no table is found in *output*.
    """
    lines = output.splitlines()

    # Locate the header row: starts with "Index" (case-insensitive)
    header_idx = None
    for i, line in enumerate(lines):
        if re.match(r"\s*Index\s", line, re.IGNORECASE):
            header_idx = i
            break

    if header_idx is None:
        raise ValueError("No .print table found in ngspice output.")

    headers = lines[header_idx].split()
    # Drop "Index" (first token); remaining are: x-axis name + signal names
    headers = headers[1:]

    data: dict[str, list[float]] = {h: [] for h in headers}

    for line in lines[header_idx + 2:]:   # +2 to skip the dashes separator
        line = line.strip()
        if not line:
            continue
        tokens = line.split()
        # Each data row: index  x_val  y1  y2 …
        if len(tokens) < len(headers) + 1:
            break
        try:
            int(tokens[0])   # first token is the row index — must be an int
        except ValueError:
            break
        for col, val in zip(headers, tokens[1:]):
            data[col].append(float(val))

    if not any(data.values()):
        raise ValueError("Table found but contains no numeric data.")

    return data


def plot(
    output: str,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    xscale: str = "linear",
    yscale: str = "linear",
    show: bool = True,
):
    """
    Plot all signals from ngspice batch output.

    Parameters
    ----------
    output:
        Raw stdout returned by :class:`~pyspice_lite.Simulator`.
    title:
        Figure title.
    xlabel:
        X-axis label (defaults to the x-column name from the table).
    ylabel:
        Y-axis label.
    xscale:
        ``"linear"`` or ``"log"``.  Defaults to ``"log"`` when the x-axis
        column is named ``"frequency"``.
    yscale:
        ``"linear"`` or ``"log"``.
    show:
        Call ``plt.show()`` when *True* (default).  Set to *False* to add
        further customisation before displaying.

    Returns
    -------
    tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(
            "matplotlib is required for plotting. Install it with: pip install matplotlib"
        ) from exc

    data = parse_print_output(output)
    columns = list(data.keys())
    x_col = columns[0]
    y_cols = columns[1:]

    x = data[x_col]

    # Auto-detect log x-scale for frequency sweeps
    if xscale == "linear" and x_col.lower() == "frequency":
        xscale = "log"

    fig, ax = plt.subplots()

    for col in y_cols:
        ax.plot(x, data[col], label=col)

    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    ax.set_xlabel(xlabel or x_col)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    if len(y_cols) > 1:
        ax.legend()

    if show:
        plt.show()

    return fig, ax
