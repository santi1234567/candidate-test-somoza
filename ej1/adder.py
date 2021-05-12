from typing import List

from nmigen import signed
from nmigen import Elaboratable, Module, Signal
from nmigen.sim import Simulator, Delay
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner

class Adder(Elaboratable):
    def __init__(self,N_bits):#, arg):
        self.a_data = Signal(signed(N_bits))
        self.b_data = Signal(signed(N_bits))
        self.r_data = Signal(signed(N_bits))



    def elaborate(self,platform:Platform) -> Module:
        m = Module()

        m.d.comb += self.r_data.eq(self.a_data + self.b_data)

        return m

    def ports(self) -> List[Signal]:
        return []

if __name__=="__main__":
    parser = main_parser()
    args = parser.parse_args()

    N_bits = 8

    m = Module()
    m.submodules.adder = adder = Adder(N_bits)

    #main_runner(parser,args,m,ports=[]+adder.ports())

    x = Signal(signed(N_bits))
    y = Signal(signed(N_bits))
    m.d.comb += adder.a_data.eq(x)
    m.d.comb += adder.b_data.eq(y)

    sim = Simulator(m)

    def process():
        yield x.eq(0x00)
        yield y.eq(0x00)
        yield Delay(1e-6)
        yield x.eq(0xFF)
        yield y.eq(0xFF)
        yield Delay(1e-6)
        yield x.eq(0x00)
        yield Delay(1e-6)

    sim.add_process(process)
    with sim.write_vcd("test.vcd","test.gtkw", traces=[x,y] + adder.ports()):
        sim.run()
