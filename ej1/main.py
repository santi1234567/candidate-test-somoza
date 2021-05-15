from nmigen_cocotb import run
from adder import Adder


if __name__ == '__main__':
    #inicializo el adder con la cantidad de bits que quiero en las entradas/salida. Luego corro los tests que se encuentran en test.py y se guarda la waveform

    core = Adder(3)
    run(
        core, 'test',
        ports=
        [
            *list(core.a.fields.values()),
            *list(core.b.fields.values()),
            *list(core.r.fields.values())
        ],
        vcd_file='adder.vcd'
    )
