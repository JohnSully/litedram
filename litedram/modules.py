from math import ceil
from collections import namedtuple

from migen import *

from litedram.common import GeomSettings, TimingSettings


_technology_timings = ["tREFI", "tWTR", "tCCD", "tRRD"]
_TechnologyTimings = namedtuple("TechnologyTimings", _technology_timings)
_speedgrade_timings = ["tRP", "tRCD", "tWR", "tRFC", "tFAW", "tRC", "tRAS"]
_SpeedgradeTimings = namedtuple("SpeedgradeTimings", _speedgrade_timings)


class SDRAMModule:
    """SDRAM module geometry and timings.

    SDRAM controller has to ensure that all geometry and
    timings parameters are fulfilled. Timings parameters
    can be expressed in ns, in SDRAM clock cycles or both
    and controller needs to use the greater value.

    SDRAM modules with the same geometry exist can have
    various speedgrades.
    """
    def __init__(self, clk_freq, rate, speedgrade=None):
        self.clk_freq = clk_freq
        self.rate = rate
        self.speedgrade = speedgrade
        self.geom_settings = GeomSettings(
            bankbits=log2_int(self.nbanks),
            rowbits=log2_int(self.nrows),
            colbits=log2_int(self.ncols),
        )
        self.timing_settings = TimingSettings(
            tRP=self.ns_to_cycles(self.get("tRP")),
            tRCD=self.ns_to_cycles(self.get("tRCD")),
            tWR=self.ns_to_cycles(self.get("tWR")),
            tREFI=self.ns_to_cycles(self.get("tREFI"), False),
            tRFC=self.ns_to_cycles(self.get("tRFC")),
            tWTR=self.ck_ns_to_cycles(*self.get("tWTR")),
            tFAW=None if self.get("tFAW") is None else self.ck_ns_to_cycles(*self.get("tFAW")),
            tCCD=None if self.get("tCCD") is None else self.ck_ns_to_cycles(*self.get("tCCD")),
            tRRD=None if self.get("tRRD") is None else self.ns_to_cycles_trrd(self.get("tRRD")),
            tRC=None if self.get("tRC") is None else self.ns_to_cycles(self.get("tRC")),
            tRAS=None if self.get("tRAS") is None else self.ns_to_cycles(self.get("tRAS"))
        )

    def get(self, name):
        if name in _speedgrade_timings:
            if hasattr(self, "speedgrade_timings"):
                speedgrade = "default" if self.speedgrade is None else self.speedgrade
                return getattr(self.speedgrade_timings[speedgrade], name)
            else:
                name = name + "_" + self.speedgrade if self.speedgrade is not None else name
                try:
                    return getattr(self, name)
                except:
                    return None
        else:
            if hasattr(self, "technology_timings"):
                return getattr(self.technology_timings, name)
            else:
                try:
                    return getattr(self, name)
                except:
                    return None


    def ns_to_cycles_trrd(self, t):
        lower_bound = {
            "1:1" : 4,
            "1:2" : 2,
            "1:4" : 1
        }
        if (t is None):
            if self.memtype == "DDR3":
                return lower_bound[self.rate]
            else:
                return 0    #Review: Is this needed for DDR2 and below?
        return max(lower_bound[self.rate], self.ns_to_cycles(t, margin=False))

    def ns_to_cycles(self, t, margin=True):
        clk_period_ns = 1e9/self.clk_freq
        if margin:
            margins = {
                "1:1" : 0,
                "1:2" : clk_period_ns/2,
                "1:4" : 3*clk_period_ns/4
            }
            t += margins[self.rate]
        return ceil(t/clk_period_ns)

    def ck_to_cycles(self, c):
        d = {
            "1:1" : 1,
            "1:2" : 2,
            "1:4" : 4
        }
        return ceil(c/d[self.rate])

    def ck_ns_to_cycles(self, c, t):
        c = 0 if c is None else c
        t = 0 if t is None else t
        return max(self.ck_to_cycles(c), self.ns_to_cycles(t))


# SDR
class IS42S16160(SDRAMModule):
    memtype = "SDR"
    # geometry
    nbanks = 4
    nrows  = 8192
    ncols  = 512
    # timings
    technology_timings = _TechnologyTimings(tREFI=64e6/8192, tWTR=(2, None), tCCD=(1, None), tRRD=None)
    speedgrade_timings = {"default": _SpeedgradeTimings(tRP=20, tRCD=20, tWR=20, tRFC=70, tFAW=None, tRC=None, tRAS=None)}


class MT48LC4M16(SDRAMModule):
    memtype = "SDR"
    # geometry
    nbanks = 4
    nrows  = 4096
    ncols  = 256
    # timings
    technology_timings = _TechnologyTimings(tREFI=64e6/8192, tWTR=(2, None), tCCD=(1, None), tRRD=None)
    speedgrade_timings = {"default": _SpeedgradeTimings(tRP=15, tRCD=15, tWR=14, tRFC=66, tFAW=None, tRC=None, tRAS=None)}


class AS4C16M16(SDRAMModule):
    memtype = "SDR"
    # geometry
    nbanks = 4
    nrows  = 8192
    ncols  = 512
    # timings
    technology_timings = _TechnologyTimings(tREFI=64e6/8192, tWTR=(2, None), tCCD=(1, None), tRRD=None)
    speedgrade_timings = {"default": _SpeedgradeTimings(tRP=18, tRCD=18, tWR=12, tRFC=60, tFAW=None, tRC=None, tRAS=None)}


# DDR
class MT46V32M16(SDRAMModule):
    memtype = "DDR"
    # geometry
    nbanks = 4
    nrows  = 8192
    ncols  = 1024
    # timings
    technology_timings = _TechnologyTimings(tREFI=64e6/8192, tWTR=(2, None), tCCD=(1, None), tRRD=None)
    speedgrade_timings = {"default": _SpeedgradeTimings(tRP=15, tRCD=15, tWR=15, tRFC=70, tFAW=None, tRC=None, tRAS=None)}


# LPDDR
class MT46H32M16(SDRAMModule):
    memtype = "LPDDR"
    # geometry
    nbanks = 4
    nrows  = 8192
    ncols  = 1024
    # timings
    technology_timings = _TechnologyTimings(tREFI=64e6/8192, tWTR=(2, None), tCCD=(1, None), tRRD=None)
    speedgrade_timings = {"default": _SpeedgradeTimings(tRP=15, tRCD=15, tWR=15, tRFC=72, tFAW=None, tRC=None, tRAS=None)}


class MT46H32M32(SDRAMModule):
    memtype = "LPDDR"
    # geometry
    nbanks = 4
    nrows  = 8192
    ncols  = 1024
    # timings
    technology_timings = _TechnologyTimings(tREFI=64e6/8192, tWTR=(2, None), tCCD=(1, None), tRRD=None)
    speedgrade_timings = {"default": _SpeedgradeTimings(tRP=15, tRCD=15, tWR=15, tRFC=72, tFAW=None, tRC=None, tRAS=None)}


# DDR2
class MT47H128M8(SDRAMModule):
    memtype = "DDR2"
    # geometry
    nbanks = 8
    nrows  = 16384
    ncols  = 1024
    # timings
    technology_timings = _TechnologyTimings(tREFI=64e6/8192, tWTR=(None, 7.5), tCCD=(2, None), tRRD=None)
    speedgrade_timings = {"default": _SpeedgradeTimings(tRP=15, tRCD=15, tWR=15, tRFC=127.5, tFAW=None, tRC=None, tRAS=None)}


class MT47H64M16(SDRAMModule):
    memtype = "DDR2"
    # geometry
    nbanks = 8
    nrows  = 8192
    ncols  = 1024
    # timings
    technology_timings = _TechnologyTimings(tREFI=64e6/8192, tWTR=(None, 7.5), tCCD=(2, None), tRRD=None)
    speedgrade_timings = {"default": _SpeedgradeTimings(tRP=15, tRCD=15, tWR=15, tRFC=127.5, tFAW=None, tRC=None, tRAS=None)}


class P3R1GE4JGF(SDRAMModule):
    memtype = "DDR2"
    # geometry
    nbanks = 8
    nrows  = 8192
    ncols  = 1024
    # timings
    technology_timings = _TechnologyTimings(tREFI=64e6/8192, tWTR=(None, 7.5), tCCD=(2, None), tRRD=None)
    speedgrade_timings = {"default": _SpeedgradeTimings(tRP=12.5, tRCD=12.5, tWR=15, tRFC=127.5, tFAW=None, tRC=None, tRAS=None)}


# DDR3 (Chips)
class MT41J128M16(SDRAMModule):
    memtype = "DDR3"
    # geometry
    nbanks = 8
    nrows  = 16384
    ncols  = 1024
    # timings
    technology_timings = _TechnologyTimings(tREFI=64e6/8192, tWTR=(4, 7.5), tCCD=(4, None), tRRD=10)
    speedgrade_timings = {
        "800": _SpeedgradeTimings(tRP=13.1, tRCD=13.1, tWR=13.1, tRFC=64, tFAW=(None, 50), tRC=50.625, tRAS=37.5),
        "1066": _SpeedgradeTimings(tRP=13.1, tRCD=13.1, tWR=13.1, tRFC=86, tFAW=(None, 50), tRC=50.625, tRAS=37.5),
        "1333": _SpeedgradeTimings(tRP=13.5, tRCD=13.5, tWR=13.5, tRFC=107, tFAW=(None, 45), tRC=49.5, tRAS=36),
        "1600": _SpeedgradeTimings(tRP=13.75, tRCD=13.75, tWR=13.75, tRFC=128, tFAW=(None, 40), tRC=48.75, tRAS=35),
    }
    speedgrade_timings["default"] = speedgrade_timings["1600"]


class MT41K128M16(MT41J128M16):
    pass


class MT41J256M16(SDRAMModule):
    memtype = "DDR3"
    # geometry
    nbanks = 8
    nrows  = 32768
    ncols  = 1024
    # timings
    technology_timings = _TechnologyTimings(tREFI=64e6/8192, tWTR=(4, 7.5), tCCD=(4, None), tRRD=10)
    speedgrade_timings = {
        "800": _SpeedgradeTimings(tRP=13.1, tRCD=13.1, tWR=13.1, tRFC=139, tFAW=(None, 50), tRC=50.625, tRAS=37.5),
        "1066": _SpeedgradeTimings(tRP=13.1, tRCD=13.1, tWR=13.1, tRFC=138, tFAW=(None, 50), tRC=50.625, tRAS=37.5),
        "1333": _SpeedgradeTimings(tRP=13.5, tRCD=13.5, tWR=13.5, tRFC=174, tFAW=(None, 45), tRC=49.5, tRAS=36),
        "1600": _SpeedgradeTimings(tRP=13.75, tRCD=13.75, tWR=13.75, tRFC=208, tFAW=(None, 40), tRC=48.75, tRAS=35),
    }
    speedgrade_timings["default"] = speedgrade_timings["1600"]


class MT41K256M16(MT41J256M16):
    pass


class K4B1G0446F(SDRAMModule):
    memtype = "DDR3"
    # geometry
    nbanks = 8
    nrows  = 16384
    ncols  = 1024
    # timings
    technology_timings = _TechnologyTimings(tREFI=64e6/8192, tWTR=(4, 7.5), tCCD=(4, None), tRRD=None)
    speedgrade_timings = {
        "800": _SpeedgradeTimings(tRP=15, tRCD=15, tWR=15, tRFC=120, tFAW=(None, 50), tRC=52.5, tRAS=37.5),
        "1066": _SpeedgradeTimings(tRP=13.125, tRCD=13.125, tWR=15, tRFC=160, tFAW=(None, 50), tRC=50.625, tRAS=37.5),
        "1333": _SpeedgradeTimings(tRP=13.5, tRCD=13.5, tWR=15, tRFC=200, tFAW=(None, 45), tRC=49.5, tRAS=36),
        "1600": _SpeedgradeTimings(tRP=13.75, tRCD=13.75, tWR=15, tRFC=240, tFAW=(None, 40), tRC=48.75, tRAS=35),
    }
    speedgrade_timings["default"] = speedgrade_timings["1600"]


# FIXME: update to new definition when fully tested (old definition still handled)
class K4B2G1646FBCK0(SDRAMModule):  ### TODO: optimize and revalidate all timings, at cold and hot temperatures
    memtype = "DDR3"
    # geometry
    nbanks = 8
    nrows  = 16384
    ncols  = 1024
    # speedgrade invariant timings
    tREFI = 7800  # 3900 refresh more often at 85C+
    tWTR  = (14, 35)
    tCCD  = (4, None)
    tRRD  = 10  # 4 * clk = 10ns
    # speedgrade related timings
    # DDR3-1600
    tRP_1600  = 13.125
    tRCD_1600 = 13.125
    tWR_1600  = 35  # this is hard-coded in MR0 to be 14 cycles, 14 * 2.5 = 35, see sdram_init.py@L224
    tRFC_1600 = 160
    tFAW_1600 = (None, 40)
    # API retro-compatibility
    tRP  = tRP_1600
    tRCD = tRCD_1600
    tWR  = tWR_1600
    tRFC = tRFC_1600
    tFAW = tFAW_1600


# DDR3 (SO-DIMM)
class MT8JTF12864(SDRAMModule):
    memtype = "DDR3"
    # geometry
    nbanks = 8
    nrows  = 16384
    ncols  = 1024
    # timings
    technology_timings = _TechnologyTimings(tREFI=64e6/8192, tWTR=(4, 7.5), tCCD=(4, None), tRRD=None)
    speedgrade_timings = {
        "1066": _SpeedgradeTimings(tRP=15, tRCD=15, tWR=15, tRFC=86, tFAW=(None, 50), tRC=None, tRAS=None),
        "1333": _SpeedgradeTimings(tRP=15, tRCD=15, tWR=15, tRFC=107, tFAW=(None, 45), tRC=None, tRAS=None),
    }
    speedgrade_timings["default"] = speedgrade_timings["1333"]


class MT18KSF1G72HZ(SDRAMModule):
    memtype = "DDR3"
    # geometry
    nbanks = 8
    nrows  = 65536
    ncols  = 1024
    # timings
    technology_timings = _TechnologyTimings(tREFI=64e6/8192, tWTR=(4, 7.5), tCCD=(4, None), tRRD=None)
    speedgrade_timings = {
        "1066": _SpeedgradeTimings(tRP=15, tRCD=15, tWR=15, tRFC=86, tFAW=(None, 50), tRC=None, tRAS=None),
        "1333": _SpeedgradeTimings(tRP=15, tRCD=15, tWR=15, tRFC=107, tFAW=(None, 45), tRC=None, tRAS=None),
        "1600": _SpeedgradeTimings(tRP=13.125, tRCD=13.125, tWR=13.125, tRFC=128, tFAW=(None, 40), tRC=None, tRAS=None),
    }
    speedgrade_timings["default"] = speedgrade_timings["1600"]
