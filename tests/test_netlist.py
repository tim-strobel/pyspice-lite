from pyspice_lite import Capacitor, Circuit, Netlist, Resistor, VoltageSource


def test_resistor_divider_netlist():
    c = Circuit("Voltage Divider")
    c.add(VoltageSource("1", "vcc", "0", dc=5.0))
    c.add(Resistor("1", "vcc", "mid", 1000.0))
    c.add(Resistor("2", "mid", "0", 1000.0))

    netlist = Netlist(c).render()

    assert "Voltage Divider" in netlist
    assert "R1 vcc mid 1000.0" in netlist
    assert "R2 mid 0 1000.0" in netlist
    assert "V1 vcc 0 DC 5.0" in netlist
    assert netlist.strip().endswith(".end")


def test_capacitor_with_initial_voltage():
    c = Circuit("RC")
    c.add(Capacitor("1", "a", "0", capacitance=1e-6, initial_voltage=3.3))
    line = c.elements[0].spice_line()
    assert "IC=3.3" in line


def test_netlist_save(tmp_path):
    c = Circuit("Test")
    c.add(Resistor("1", "a", "b", 100.0))
    path = str(tmp_path / "out.cir")
    Netlist(c).save(path)
    with open(path) as f:
        content = f.read()
    assert "R1 a b 100.0" in content
