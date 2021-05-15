from nmigen import *
import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
#Copiada de example.py | Stream define el flujo de una entrada/salida con sus respectivas señales y tiene algunas funcionalidades extras.
#Cambie width por n_bits y data paso a ser signada.
class Stream(Record):
    def __init__(self, n_bits, **kwargs):
        Record.__init__(self, [('data', signed(n_bits)), ('valid', 1), ('ready', 1)], **kwargs)

    def accepted(self):
        return self.valid & self.ready

    class Driver:
        def __init__(self, clk, dut, prefix):
            self.clk = clk
            self.data = getattr(dut, prefix + 'data')
            self.valid = getattr(dut, prefix + 'valid')
            self.ready = getattr(dut, prefix + 'ready')

        async def send(self, data):
            self.valid <= 1
            for d in data:
                self.data <= d
                await RisingEdge(self.clk)
                while self.ready.value == 0:
                    await RisingEdge(self.clk)
            self.valid <= 0

        async def recv(self, count):
            self.ready <= 1
            data = []
            for _ in range(count):
                await RisingEdge(self.clk)
                while self.valid.value == 0:
                    await RisingEdge(self.clk)
                data.append(self.data.value.integer)
            self.ready <= 0
            return data
