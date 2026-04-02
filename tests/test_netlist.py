from pyspice_lite import BJT, Capacitor, Circuit, JFET, Library, ModelCard, MOSFET, Netlist, Resistor, VoltageSource


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


def test_library_without_section():
    lib = Library("/path/to/pdk.lib")
    assert lib.spice_line() == '.lib "/path/to/pdk.lib"'


def test_library_with_section():
    lib = Library("/path/to/pdk.lib", section="tt")
    assert lib.spice_line() == '.lib "/path/to/pdk.lib" tt'


def test_library_in_netlist():
    c = Circuit("BSIM Circuit")
    c.add(Library("/path/to/tsmc65.lib", section="tt"))
    c.add(VoltageSource("dd", "vdd", "0", dc=1.8))
    netlist = Netlist(c).render()
    assert '.lib "/path/to/tsmc65.lib" tt' in netlist
    assert netlist.index('.lib') < netlist.index('Vdd')  # lib comes first


def test_bjt_spice_line():
    q = BJT("1", collector="vcc", base="vin", emitter="0", model="Q2N2222")
    assert q.spice_line() == "Q1 vcc vin 0 Q2N2222"


def test_bjt_with_substrate_and_area():
    q = BJT("2", collector="c", base="b", emitter="e", model="QMOD", substrate="sub", area=2.0)
    assert q.spice_line() == "Q2 c b e sub QMOD 2.0"


def test_mosfet_spice_line():
    m = MOSFET("1", drain="d", gate="g", source="s", bulk="0", model="NMOS1", w=10e-6, l=1e-6)
    assert m.spice_line() == "M1 d g s 0 NMOS1 W=1e-05 L=1e-06"


def test_mosfet_without_wl():
    m = MOSFET("2", drain="d", gate="g", source="s", bulk="0", model="PMOS1")
    assert m.spice_line() == "M2 d g s 0 PMOS1"


def test_jfet_spice_line():
    j = JFET("1", drain="d", gate="g", source="s", model="J2N3819")
    assert j.spice_line() == "J1 d g s J2N3819"


def test_model_card_spice_line():
    mc = ModelCard("Q2N2222", model_type="NPN", params={"IS": 1e-14, "BF": 100})
    line = mc.spice_line()
    assert line.startswith(".model Q2N2222 NPN")
    assert "IS=1e-14" in line
    assert "BF=100" in line


def test_bjt_common_emitter_netlist():
    c = Circuit("BJT CE Amplifier")
    c.add(ModelCard("Q2N2222", model_type="NPN", params={"BF": 200}))
    c.add(VoltageSource("cc", "vcc", "0", dc=12.0))
    c.add(Resistor("c", "vcc", "col", 1000.0))
    c.add(BJT("1", collector="col", base="base", emitter="0", model="Q2N2222"))

    netlist = Netlist(c).render()
    assert ".model Q2N2222 NPN" in netlist
    assert "Q1 col base 0 Q2N2222" in netlist
    assert netlist.strip().endswith(".end")


def test_netlist_save(tmp_path):
    c = Circuit("Test")
    c.add(Resistor("1", "a", "b", 100.0))
    path = str(tmp_path / "out.cir")
    Netlist(c).save(path)
    with open(path) as f:
        content = f.read()
    assert "R1 a b 100.0" in content
