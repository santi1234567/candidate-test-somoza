from nmigen import *
from nmigen_cocotb import run
from nmigen.build import Platform
import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
from random import getrandbits


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



class Adder(Elaboratable):
    def __init__(self,n_bits):#, arg):
        self.a = Stream(n_bits, name='a')
        self.b = Stream(n_bits, name='b')
        self.r = Stream(n_bits, name='r')



    def elaborate(self,platform:Platform) -> Module:
        # m = Module()
        #
        # m.d.comb += self.r_data.eq(self.a_data + self.b_data)
        #
        # return m
        m = Module()
        sync = m.d.sync
        comb = m.d.comb
        comb += self.b.data.eq(0)

        comb += self.a.data.eq(0)
        #inicializo la salida cero para esperar a que las entradas esten habilitadas
        with m.If(self.r.accepted()):
            sync += self.r.valid.eq(0)

        with m.If(self.a.accepted()&self.b.accepted()):
            sync += [
                self.r.valid.eq(1),
                self.r.data.eq(self.a.data + self.b.data)
            ]
        comb += self.a.ready.eq((~self.r.valid) | (self.r.accepted()))
        comb += self.b.ready.eq((~self.r.valid) | (self.r.accepted()))
        return m

async def init_test(dut):
    cocotb.fork(Clock(dut.clk, 10, 'ns').start())
    dut.rst <= 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst <= 0

@cocotb.test()
async def burst(dut):
	await init_test(dut)
	stream_input_b = Stream.Driver(dut.clk, dut, 'b__')
	stream_input_a = Stream.Driver(dut.clk, dut, 'a__')

	stream_output = Stream.Driver(dut.clk, dut, 'r__')

	N = 100
	width = len(dut.a__data)
	mask = int('1' * width, 2)

	data_1 = [getrandbits(width) for _ in range(N)]
	data_2 = [getrandbits(width) for _ in range(N)]
	expected = []

	for d in range(1,N+1):
		expected.append(data_1[d-1]+data_2[d-1])
		
		#Trunco a la cantidad de bits que se usa cuando hay overflow
		expected[-1]= (expected[-1]- 2**width) if expected[-1] > (2**width-1) else expected[-1]
		#print(hex(data_1[d-1]),"+",hex(data_2[d-1]),"=",hex(expected[-1]))
	cocotb.fork(stream_input_a.send(data_1))
	cocotb.fork(stream_input_b.send(data_2))

	recved = await stream_output.recv(N)
	#print(hex(expected[0]),hex(expected[1]), hex(expected[-1]))
	#print(hex(recved[0]),hex(recved[1]), hex(recved[-1]))
	assert recved == expected

###testeo todas las posibles combinaciones de entrada y salida. Es un test bastante pesado para N grande
@cocotb.test()
async def todas(dut):
	await burst(dut)

	stream_input_b = Stream.Driver(dut.clk, dut, 'b__')

	stream_input_a = Stream.Driver(dut.clk, dut, 'a__')

	stream_output = Stream.Driver(dut.clk, dut, 'r__')


	width = len(dut.a__data) 
	mask = int('1' * width, 2)    
	data_1=[]
	data_2=[]
	for y in range(2**width):
		for x in range(2**width):
			data_1.append(y)
			data_2.append(x)

	expected = []

	for d in range(1,2**(2*width)+1):
		expected.append(data_1[d-1]+data_2[d-1])
		
		#Trunco a la cantidad de bits que se usa cuando hay overflow
		expected[-1]= (expected[-1]- 2**width) if expected[-1] > (2**width-1) else expected[-1]
		#print(hex(data_1[d-1]),"+",hex(data_2[d-1]),"=",hex(expected[-1]))
	cocotb.fork(stream_input_a.send(data_1))
	cocotb.fork(stream_input_b.send(data_2))

	recved = await stream_output.recv(2**(2*width))


	stream_input_b = Stream.Driver(dut.clk, dut, 'b__')

	stream_input_a = Stream.Driver(dut.clk, dut, 'a__')

	stream_output = Stream.Driver(dut.clk, dut, 'r__')

  
	data_1=[]
	data_2=[]
	for y in range(2**width):
		for x in range(2**width):
			data_2.append(y)
			data_1.append(x)

	expected = []

	for d in range(1,2**(2*width)+1):
		expected.append(data_1[d-1]+data_2[d-1])
		
		#Trunco a la cantidad de bits que se usa cuando hay overflow
		expected[-1]= (expected[-1]- 2**width) if expected[-1] > (2**width-1) else expected[-1]
		#print(hex(data_1[d-1]),"+",hex(data_2[d-1]),"=",hex(expected[-1]))
	cocotb.fork(stream_input_a.send(data_1))
	cocotb.fork(stream_input_b.send(data_2))

	recved = await stream_output.recv(2**(2*width))
	#print(hex(expected[0]),hex(expected[1]), hex(expected[-1]))
	#print(hex(recved[0]),hex(recved[1]), hex(recved[-1]))
	assert recved == expected


if __name__ == '__main__':
    core = Adder(4)
    run(
        core, 'adder',
        ports=
        [
            *list(core.a.fields.values()),
            *list(core.b.fields.values()),
            *list(core.r.fields.values())
        ],
        vcd_file='adder.vcd'
    )
