import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
from random import getrandbits
from adder import Adder
from stream import Stream

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

	data_a = [getrandbits(width) for _ in range(N)]
	data_b = [getrandbits(width) for _ in range(N)]
	expected = []

	for d in range(1,N+1):
		expected.append(data_a[d-1]+data_b[d-1])
		
		#Trunco a la cantidad de bits que se usa cuando hay overflow
		expected[-1]= (expected[-1]- 2**width) if expected[-1] > (2**width-1) else expected[-1]

	cocotb.fork(stream_input_a.send(data_a))
	cocotb.fork(stream_input_b.send(data_b))

	recved = await stream_output.recv(N)

	assert recved == expected

###testeo todas las posibles combinaciones de entrada y salida. Es un test bastante pesado para width grande grande
@cocotb.test()
async def todas_las_comb(dut):
	await burst(dut)

	stream_input_b = Stream.Driver(dut.clk, dut, 'b__')

	stream_input_a = Stream.Driver(dut.clk, dut, 'a__')

	stream_output = Stream.Driver(dut.clk, dut, 'r__')


	width = len(dut.a__data) 

	data_a=[]
	data_b=[]
	#lleno las entradas con todas las posibles combinaciones
	for y in range(2**width):
		for x in range(2**width):
			data_a.append(y)
			data_b.append(x)
	expected = []

	for d in range(1,2**(2*width)+1):
		expected.append(data_a[d-1]+data_b[d-1])
		
		#Trunco a la cantidad de bits que se usa cuando hay overflow
		expected[-1]= (expected[-1]- 2**width) if expected[-1] > (2**width-1) else expected[-1]
	cocotb.fork(stream_input_a.send(data_a))
	cocotb.fork(stream_input_b.send(data_b))

	recved = await stream_output.recv(2**(2*width))
	assert recved == expected