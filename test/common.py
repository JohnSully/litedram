from migen import *


def seed_to_data(seed, random=True, nbits=32):
    if nbits == 32:
        if random:
            return (seed * 0x31415979 + 1) & 0xffffffff
        else:
            return seed
    else:
        assert nbits%32 == 0
        data = 0
        for i in range(nbits//32):
            data = data << 32
            data |= seed_to_data(seed*nbits//32 + i, random, 32)
        return data


class DRAMMemory:
    def __init__(self, width, depth, init=[]):
        self.width = width
        self.depth = depth
        self.mem = []
        for d in init:
            self.mem.append(d)
        for _ in range(depth-len(init)):
            self.mem.append(0)

    def show_content(self):
        for addr in range(self.depth):
            print("0x{:08x}: 0x{:08x}".format(addr, self.mem[addr]))

    @passive
    def read_handler(self, dram_port):
        address = 0
        pending = 0
        yield dram_port.cmd.ready.eq(0)
        while True:
            yield dram_port.rdata.valid.eq(0)
            if pending:
                yield dram_port.rdata.valid.eq(1)
                yield dram_port.rdata.data.eq(self.mem[address%self.depth])
                yield
                yield dram_port.rdata.valid.eq(0)
                yield dram_port.rdata.data.eq(0)
                pending = 0
            elif (yield dram_port.cmd.valid):
                pending = not (yield dram_port.cmd.we)
                address = (yield dram_port.cmd.addr)
                if pending:
                    yield dram_port.cmd.ready.eq(1)
                    yield
                    yield dram_port.cmd.ready.eq(0)
            yield

    @passive
    def write_handler(self, dram_port):
        address = 0
        pending = 0
        yield dram_port.cmd.ready.eq(0)
        while True:
            yield dram_port.wdata.ready.eq(0)
            if pending:
                while (yield dram_port.wdata.valid) == 0:
                    yield
                yield dram_port.wdata.ready.eq(1)
                yield
                self.mem[address%self.depth] = (yield dram_port.wdata.data) # TODO manage we
                yield dram_port.wdata.ready.eq(0)
                yield
                pending = 0
                yield
            elif (yield dram_port.cmd.valid):
                pending = (yield dram_port.cmd.we)
                address = (yield dram_port.cmd.addr)
                if pending:
                    yield dram_port.cmd.ready.eq(1)
                    yield
                    yield dram_port.cmd.ready.eq(0)
            yield
