from nmigen import *
from nmigen_cocotb import run
from nmigen.build import Platform
from stream import Stream

class Adder(Elaboratable):
    def __init__(self,n_bits):#, arg):
        self.a = Stream(n_bits, name='a')
        self.b = Stream(n_bits, name='b')
        #opto por definir que la salida tiene el mismo numero de bits que las entradas
        self.r = Stream(n_bits, name='r')



    def elaborate(self,platform:Platform) -> Module:
        m = Module()
        sync = m.d.sync
        comb = m.d.comb
        comb += self.b.data.eq(0)

        comb += self.a.data.eq(0)



        with m.If(self.a.accepted()&self.b.accepted()): #si esta todo bien en las entradas, se saca una salida
            sync += [
                self.r.valid.eq(1),
                self.r.data.eq(self.a.data + self.b.data)
            ]
        with m.Else(): #salida no valida si hay algun problema en una entrada. se saca un cero por defecto
        	sync += self.r.valid.eq(0)
        	sync += self.r.data.eq(0)


        comb += self.a.ready.eq((~self.r.valid) | (self.r.accepted()))
        comb += self.b.ready.eq((~self.r.valid) | (self.r.accepted()))
        return m

