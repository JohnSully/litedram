from migen import *

from litex.soc.interconnect.csr import *


class Bandwidth(Module, AutoCSR):
    def __init__(self, cmdReadWrite, cmdActPrecharge, data_width, period_bits=24):
        self.update = CSR()
        self.nreads = CSRStatus(period_bits)
        self.nwrites = CSRStatus(period_bits)
        self.nactivates = CSRStatus(period_bits)
        self.data_width = CSRStatus(bits_for(data_width), reset=data_width)

        # # #

        cmd_valid = Signal()
        cmd_ready = Signal()
        cmd_is_read = Signal()
        cmd_is_write = Signal()

        cmdAct_valid = Signal()
        cmdAct_ready = Signal()
        cmdAct_isAct = Signal()
        self.sync += [
            cmd_valid.eq(cmdReadWrite.valid),
            cmd_ready.eq(cmdReadWrite.ready),
            cmd_is_read.eq(cmdReadWrite.is_read),
            cmd_is_write.eq(cmdReadWrite.is_write),

            cmdAct_valid.eq(cmdActPrecharge.valid),
            cmdAct_ready.eq(cmdActPrecharge.ready),
            cmdAct_isAct.eq(cmdActPrecharge.ras & ~cmdActPrecharge.cas & ~cmdActPrecharge.we),
        ]

        counter = Signal(period_bits)
        period = Signal()
        nreads = Signal(period_bits)
        nwrites = Signal(period_bits)
        nacts = Signal(period_bits)
        nreads_r = Signal(period_bits)
        nwrites_r = Signal(period_bits)
        nacts_r = Signal(period_bits)

        self.sync += [
            Cat(counter, period).eq(counter + 1),
            If(period,
                nreads_r.eq(nreads),
                nwrites_r.eq(nwrites),
                nacts_r.eq(nacts),
                nreads.eq(0),
                nwrites.eq(0),
                nacts.eq(0),
            ).Else(
                If(cmd_valid & cmd_ready,
                    If(cmd_is_read, nreads.eq(nreads + 1)),
                    If(cmd_is_write, nwrites.eq(nwrites + 1)),
                ),
                If(cmdAct_valid & cmdAct_ready,
                    If(cmdAct_isAct, nacts.eq(nacts + 1))
                )
            ),
            If(self.update.re,
                self.nreads.status.eq(nreads_r),
                self.nwrites.status.eq(nwrites_r),
                self.nactivates.status.eq(nacts_r),
            )
        ]
