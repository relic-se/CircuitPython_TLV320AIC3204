# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2026 Cooper Dalrymple
#
# SPDX-License-Identifier: MIT
"""
`relic_tlv320aic3204`
================================================================================

Driver library for the TLV320AIC3204 audio codec


* Author(s): Cooper Dalrymple

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
* Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

import time

import digitalio
import microcontroller
import pwmio
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_register.i2c_bit import RWBit as _RWBit
from adafruit_register.i2c_bits import RWBits as _RWBits
from busio import I2C
from micropython import const

try:
    from typing import Optional, Type

    from circuitpython_typing.device_drivers import I2CDeviceDriver
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/relic-se/CircuitPython_TLV320AIC3204.git"

# I2C address
_DEFAULT_I2C_ADDR = const(0x18)

_REG_PAGE = const(0x00)

# Page 0 Registers
_REG_SOFTWARE_RESET = const(0x01)
_REG_CLOCK_1 = const(0x04)
_REG_CLOCK_2 = const(0x05)
_REG_CLOCK_3 = const(0x06)
_REG_CLOCK_4 = const(0x07)
_REG_CLOCK_5 = const(0x08)
_REG_NDAC = const(0x0B)
_REG_MDAC = const(0x0C)
_REG_DAC_OSR_MSB = const(0x0D)
_REG_DAC_OSR_LSB = const(0x0E)
_REG_ADC_OSR = const(0x14)
_REG_AUDIO_INTERFACE_1 = const(0x1B)
_REG_AUDIO_INTERFACE_3 = const(0x1D)
_REG_DAC_PROCESSING_BLOCK = const(0x3C)
_REG_ADC_PROCESSING_BLOCK = const(0x3D)
_REG_DAC_CHANNEL_1 = const(0x3F)
_REG_DAC_CHANNEL_2 = const(0x40)
_REG_LEFT_DAC_VOLUME = const(0x41)
_REG_RIGHT_DAC_VOLUME = const(0x42)
_REG_ADC_CHANNEL_1 = const(0x51)
_REG_ADC_CHANNEL_2 = const(0x52)
_REG_LEFT_ADC_VOLUME = const(0x53)
_REG_RIGHT_ADC_VOLUME = const(0x54)

# Page 1 Registers
_REG_POWER_CONFIG = const(0x01)
_REG_LDO_CONTROL = const(0x02)
_REG_OUTPUT_DRIVER_POWER = const(0x09)
_REG_COMMON_MODE = const(0x0A)
_REG_HPL_ROUTING = const(0x0C)
_REG_HPR_ROUTING = const(0x0D)
_REG_LOL_ROUTING = const(0x0E)
_REG_LOR_ROUTING = const(0x0F)
_REG_HPL_GAIN = const(0x10)
_REG_HPR_GAIN = const(0x11)
_REG_LOL_GAIN = const(0x12)
_REG_LOR_GAIN = const(0x13)
_REG_IN1L_TO_HPL_VOLUME = const(0x16)
_REG_IN1R_TO_HPR_VOLUME = const(0x17)
_REG_MIXER_LEFT_VOLUME = const(0x18)
_REG_MIXER_RIGHT_VOLUME = const(0x19)
_REG_MICBIAS = const(0x33)
_REG_LEFT_MICPGA_POS = const(0x34)
_REG_LEFT_MICPGA_NEG = const(0x36)
_REG_RIGHT_MICPGA_POS = const(0x37)
_REG_RIGHT_MICPGA_NEG = const(0x39)
_REG_FLOATING_INPUT = const(0x3A)
_REG_LEFT_MICPGA_GAIN = const(0x3B)
_REG_RIGHT_MICPGA_GAIN = const(0x3C)
_REG_MIC_POWERUP = const(0x47)
_REG_REF_POWERUP = const(0x7B)

AUDIO_INTERFACE_I2S = const(0b00)
AUDIO_INTERFACE_DSP = const(0b01)
AUDIO_INTERFACE_RJF = const(0b10)
AUDIO_INTERFACE_LJF = const(0b11)

_PLL_CLKIN_MCLK = const(0b00)
_PLL_CLKIN_BCLK = const(0b01)
_PLL_CLKIN_GPIO = const(0b10)
_PLL_CLKIN_DIN = const(0b11)

_CODEC_CLKIN_MCLK = const(0b00)
_CODEC_CLKIN_BCLK = const(0b01)
_CODEC_CLKIN_GPIO = const(0b10)
_CODEC_CLKIN_PLL = const(0b11)

_ADC_OSR_256 = const(0b00000000)
_ADC_OSR_32 = const(0b00100000)
_ADC_OSR_64 = const(0b01000000)
_ADC_OSR_128 = const(0b10000000)

DAC_PATH_DISABLED = const(0b00)
DAC_PATH_NORMAL = const(0b01)
DAC_PATH_SWAPPED = const(0b10)
DAC_PATH_MIXED = const(0b11)

_REF_POWERUP_SLOW = const(0b000)
_REF_POWERUP_40MS = const(0b001)
_REF_POWERUP_80MS = const(0b010)
_REF_POWERUP_120MS = const(0b011)
_REF_FORCE_POWERUP_SLOW = const(0b100)
_REF_FORCE_POWERUP_40MS = const(0b101)
_REF_FORCE_POWERUP_80MS = const(0b110)
_REF_FORCE_POWERUP_120MS = const(0b111)

_MIC_POWERUP_3_1MS = const(0b01)
_MIC_POWERUP_6_4MS = const(0b10)
_MIC_POWERUP_1_6MS = const(0b11)

_SOURCE_AVDD = const(0)
_SOURCE_LDOIN = const(1)

MICBIAS_MODE_1V25 = const(0b00)
MICBIAS_MODE_1V7 = const(0b01)
MICBIAS_MODE_2V5 = const(0b10)
MICBIAS_MODE_SOURCE = const(0b11)

MIC_INPUT_1 = const(0)
MIC_INPUT_2 = const(1)
MIC_INPUT_3 = const(2)

MIC_DISCONNECTED = const(0b00)
MIC_IMPEDANCE_10K = const(0b01)
MIC_IMPEDANCE_20K = const(0b01)
MIC_IMPEDANCE_40K = const(0b01)

_UINT7_VOLUME_TABLE = (
    0,  #       0  Begin linear segment: round((-1.99 * dB) - 0.2)
    -0.5,  #    1
    -1,  #      2
    -1.5,  #    3
    -2,  #      4
    -2.5,  #    5
    -3,  #      6
    -3.5,  #    7
    -4,  #      8
    -4.5,  #    9
    -5,  #     10
    -5.5,  #   11
    -6,  #     12
    -6.5,  #   13
    -7,  #     14
    -7.5,  #   15
    -8,  #     16
    -8.5,  #   17
    -9,  #     18
    -9.5,  #   19
    -10,  #    20
    -10.5,  #  21
    -11,  #    22
    -11.5,  #  23
    -12,  #    24
    -12.5,  #  25
    -13,  #    26
    -13.5,  #  27
    -14,  #    28
    -14.5,  #  29
    -15,  #    30
    -15.5,  #  31
    -16,  #    32
    -16.5,  #  33
    -17,  #    34
    -17.5,  #  35
    -18.1,  #  36
    -18.6,  #  37
    -19.1,  #  38
    -19.6,  #  39
    -20.1,  #  40
    -20.6,  #  41
    -21.1,  #  42
    -21.6,  #  43
    -22.1,  #  44
    -22.6,  #  45
    -23.1,  #  46
    -23.6,  #  47
    -24.1,  #  48
    -24.6,  #  49
    -25.1,  #  50
    -25.6,  #  51
    -26.1,  #  52
    -26.6,  #  53
    -27.1,  #  54
    -27.6,  #  55
    -28.1,  #  56
    -28.6,  #  57
    -29.1,  #  58
    -29.6,  #  59
    -30.1,  #  60
    -30.6,  #  61
    -31.1,  #  62
    -31.6,  #  63
    -32.1,  #  64
    -32.6,  #  65
    -33.1,  #  66
    -33.6,  #  67
    -34.1,  #  68
    -34.6,  #  69
    -35.2,  #  70
    -35.7,  #  71
    -36.2,  #  72
    -36.7,  #  73
    -37.2,  #  74
    -37.7,  #  75
    -38.2,  #  76
    -38.7,  #  77
    -39.2,  #  78
    -39.7,  #  79
    -40.2,  #  80
    -40.7,  #  81
    -41.2,  #  82
    -41.7,  #  83
    -42.1,  #  84
    -42.7,  #  85
    -43.2,  #  86
    -43.8,  #  87
    -44.3,  #  88
    -44.8,  #  89
    -45.2,  #  90
    -45.8,  #  91
    -46.2,  #  92
    -46.7,  #  93
    -47.4,  #  94
    -47.9,  #  95
    -48.2,  #  96
    -48.7,  #  97
    -49.3,  #  98
    -50,  #    99
    -50.3,  # 100
    -51,  #   101
    -51.4,  # 102
    -51.8,  # 103
    -52.2,  # 104
    -52.7,  # 105  End linear segment: round((-1.99 * dB) - 0.2)
    -53.7,  # 106  Begin curved segment
    -54.2,  # 107
    -55.3,  # 108
    -56.7,  # 109
    -58.3,  # 110
    -60.2,  # 111
    -62.7,  # 112
    -64.3,  # 113
    -66.2,  # 114
    -68.7,  # 115
    -72.2,  # 116  End curved segment
    -78.3,  # 117  Begin constant segment -78.3 dB
)

_UINT6_VOLUME_TABLE = (
    0.0,
    -0.4,
    -0.9,
    -1.3,
    -1.8,
    -2.3,
    -2.9,
    -3.3,
    -3.9,
    -4.3,
    -4.8,
    -5.2,
    -5.8,
    -6.3,
    -6.6,
    -7.2,
    -7.8,
    -8.2,
    -8.5,
    -9.3,
    -9.7,
    -10.1,
    -10.6,
    -11.0,
    -11.5,
    -12.0,
    -12.6,
    -13.2,
    -13.8,
    -14.5,
    -15.3,
    -16.1,
    -17.0,
    -18.1,
    -19.2,
    -20.6,
    -22.1,
    -24.1,
    -26.6,
    -30.1,
)


class RWBit(_RWBit):
    def __init__(  # noqa: PLR0913
        self,
        page: int,
        register_address: int,
        bit: int,
        register_width: int = 1,
        lsb_first: bool = True,
    ):
        super().__init__(register_address, bit, register_width, lsb_first)
        self._page = page

    def __get__(
        self, obj: Optional[I2CDeviceDriver], objtype: Optional[Type[I2CDeviceDriver]] = None
    ) -> bool:
        obj._page = self._page
        return super().__get__(obj, objtype)

    def __set__(self, obj: I2CDeviceDriver, value: bool):
        obj._page = self._page
        super().__set__(obj, bool(value))


class RWBits(_RWBits):
    def __init__(  # noqa: PLR0913, PLR0917
        self,
        page: int,
        num_bits: int,
        register_address: int,
        lowest_bit: int,
        register_width: int = 1,
        lsb_first: bool = True,
        signed: bool = False,
    ):
        super().__init__(num_bits, register_address, lowest_bit, register_width, lsb_first, signed)
        self._page = page

    def __get__(
        self, obj: Optional[I2CDeviceDriver], objtype: Optional[Type[I2CDeviceDriver]] = None
    ) -> int:
        obj._page = self._page
        return super().__get__(obj, objtype)

    def __set__(self, obj: I2CDeviceDriver, value: int):
        obj._page = self._page
        super().__set__(obj, int(value))


class CacheBits(_RWBits):
    def __init__(  # noqa: PLR0913, PLR0917
        self,
        num_bits: int,
        register_address: int,
        lowest_bit: int,
        register_width: int = 1,
        lsb_first: bool = True,
        signed: bool = False,
    ):
        super().__init__(num_bits, register_address, lowest_bit, register_width, lsb_first, signed)
        self._value = None

    def __get__(
        self, obj: Optional[I2CDeviceDriver], objtype: Optional[Type[I2CDeviceDriver]] = None
    ) -> int:
        return super().__get__(obj, objtype) if self._value is None else self._value

    def __set__(self, obj: I2CDeviceDriver, value: int):
        self._value = value
        super().__set__(obj, int(value))


class VolumeBits(RWBits):
    def __init__(self, page: int, register_address: int, table: tuple, mute: bool = False):
        super().__init__(page, 7, register_address, 0)
        self._table = table
        self._mute = mute

    def __get__(
        self, obj: Optional[I2CDeviceDriver], objtype: Optional[Type[I2CDeviceDriver]] = None
    ):
        value = super().__get__(obj, objtype)
        if self._mute and value >= len(self._table):
            return -99.9
        else:
            return self._table[min(max(value, 0), len(self._table) - 1)]

    def __set__(self, obj: I2CDeviceDriver, value: int):
        value = min(max(value, self._table[-1]), self._table[0])
        for i, db in enumerate(self._table):
            if value >= db:
                value = i
                break
        if isinstance(value, float):
            value = len(self._table) - (0 if self._mute else 1)
        super().__set__(obj, value)


class TLV320AIC3204:  # noqa: PLR0904
    _page: int = CacheBits(8, _REG_PAGE, 0)

    def __init__(
        self,
        i2c: I2C,
        mclk: microcontroller.Pin = None,
        rst: microcontroller.Pin = None,
        address: int = _DEFAULT_I2C_ADDR,
    ) -> None:
        self.i2c_device: I2CDevice = I2CDevice(i2c, address)

        self._mclk = (
            pwmio.PWMOut(mclk, frequency=15_000_000, duty_cycle=2**15) if mclk is not None else None
        )

        if rst is not None:
            self._reset = digitalio.DigitalInOut(rst)
            self._reset.direction = digitalio.Direction.OUTPUT
            self._reset.value = True
        else:
            self._reset = RWBit(0, _REG_SOFTWARE_RESET, 0)
        self.reset()

        # Power Configuration (See Figure 21)
        self._power_isolation = True
        self._avdd_ldo_enabled = True
        self._reference_powerup = _REF_POWERUP_40MS
        self._mic_powerup = _MIC_POWERUP_3_1MS
        self._analog_block_power_disabled = False
        self._line_output_power_source = _SOURCE_LDOIN
        self._headphone_output_ldoin_3v3 = True
        self._headphone_output_power_source = _SOURCE_LDOIN

        self.dac_volume = -63.5
        self.adc_volume = -12.0

        self.sample_rate = 44100
        self.bit_depth = 16

    def reset(self) -> None:
        if isinstance(self._reset, digitalio.DigitalInOut):
            self._reset.value = False
            time.sleep(0.002)
            self._reset.value = True
            time.sleep(0.002)
        else:
            self._reset = True
        time.sleep(0.01)

    _power_isolation: bool = RWBit(1, _REG_POWER_CONFIG, 3)

    _analog_block_power_disabled: bool = RWBit(1, _REG_LDO_CONTROL, 3)

    _avdd_ldo_enabled: bool = RWBit(1, _REG_LDO_CONTROL, 0)

    _reference_powerup: int = RWBits(1, 3, _REG_REF_POWERUP, 0)

    _mic_powerup: int = RWBits(1, 6, _REG_MIC_POWERUP, 0)

    _line_output_power_source: bool = RWBit(1, _REG_COMMON_MODE, 3)

    _headphone_output_ldoin_3v3: bool = RWBit(1, _REG_COMMON_MODE, 0)

    _headphone_output_power_source: bool = RWBit(1, _REG_COMMON_MODE, 3)

    audio_interface: int = RWBits(0, 2, _REG_AUDIO_INTERFACE_1, 6)

    _bit_depth: int = RWBits(0, 2, _REG_AUDIO_INTERFACE_1, 4)

    @property
    def bit_depth(self) -> int:
        """The number of bits per sample. The values 16, 20, 24, and 32 are supported.

        :default: 16
        """
        return 16 + self._bit_depth * 4

    @bit_depth.setter
    def bit_depth(self, value: int) -> None:
        if value != 16:
            raise ValueError("CircuitPython I2S only supports 16-bit stereo")
        self._bit_depth = (value - 16) // 4

    dac_loopback: bool = RWBit(0, _REG_AUDIO_INTERFACE_3, 5)
    """If set as `True`, DAC input is routed to ADC output."""

    adc_loopback: bool = RWBit(0, _REG_AUDIO_INTERFACE_3, 4)
    """If set as `True`, ADC output is routed to DAC input."""

    left_dac_enabled: bool = RWBit(0, _REG_DAC_CHANNEL_1, 7)
    right_dac_enabled: bool = RWBit(0, _REG_DAC_CHANNEL_1, 6)

    @property
    def dac_enabled(self) -> bool:
        return self.left_dac_enabled or self.right_dac_enabled

    @dac_enabled.setter
    def dac_enabled(self, value: bool) -> None:
        self.left_dac_enabled = value
        self.right_dac_enabled = value

    dac_processing_block: int = RWBits(0, 5, _REG_DAC_PROCESSING_BLOCK, 0)
    adc_processing_block: int = RWBits(0, 5, _REG_ADC_PROCESSING_BLOCK, 0)

    left_dac_path: int = RWBits(0, 2, _REG_DAC_CHANNEL_1, 4)
    right_dac_path: int = RWBits(0, 2, _REG_DAC_CHANNEL_1, 2)

    @property
    def dac_path(self) -> int:
        return self.left_dac_path

    @dac_path.setter
    def dac_path(self, value: int) -> None:
        self.left_dac_path = value
        self.right_dac_path = value

    left_dac_muted: bool = RWBit(0, _REG_DAC_CHANNEL_2, 3)
    right_dac_muted: bool = RWBit(0, _REG_DAC_CHANNEL_2, 2)

    @property
    def dac_muted(self) -> bool:
        return self.left_dac_muted or self.right_dac_muted

    @dac_muted.setter
    def dac_muted(self, value: bool) -> None:
        self.left_dac_muted = value
        self.right_dac_muted = value

    _left_dac_volume: int = RWBits(0, 8, _REG_LEFT_DAC_VOLUME, 0, signed=True)

    @property
    def left_dac_volume(self) -> float:
        return self._left_dac_volume / 2

    @left_dac_volume.setter
    def left_dac_volume(self, value: float) -> None:
        self._left_dac_volume = min(max(round(value * 2), -127), 48)

    _right_dac_volume: int = RWBits(0, 8, _REG_RIGHT_DAC_VOLUME, 0, signed=True)

    @property
    def right_dac_volume(self) -> float:
        return self._right_dac_volume / 2

    @right_dac_volume.setter
    def right_dac_volume(self, value: float) -> None:
        self._right_dac_volume = min(max(round(value * 2), -127), 48)

    @property
    def dac_volume(self) -> float:
        return self.left_dac_volume

    @dac_volume.setter
    def dac_volume(self, value: float) -> None:
        self.left_dac_volume = value
        self.right_dac_volume = value

    _pll_enabled: bool = RWBit(0, _REG_CLOCK_2, 7)
    _pll_p: int = RWBits(0, 3, _REG_CLOCK_2, 4)
    _pll_r: int = RWBits(0, 3, _REG_CLOCK_2, 0)
    _pll_j: int = RWBits(0, 6, _REG_CLOCK_3, 0)

    _pll_d_msb: int = RWBits(0, 6, _REG_CLOCK_4, 0)
    _pll_d_lsb: int = RWBits(0, 8, _REG_CLOCK_5, 0)

    @property
    def _pll_d(self) -> int:
        return self._pll_d_lsb | (self._pll_d_msb << 8)

    @_pll_d.setter
    def _pll_d(self, value: int) -> None:
        self._pll_d_lsb = value & 0xFF
        self._pll_d_msb = (value >> 8) & 0x3F

    _pll_clkin: int = RWBits(0, 2, _REG_CLOCK_1, 2)

    _codec_clkin: int = RWBits(0, 2, _REG_CLOCK_1, 0)

    _ndac_enabled: bool = RWBit(0, _REG_NDAC, 7)

    _ndac: int = RWBits(0, 7, _REG_NDAC, 0)

    _mdac_enabled: bool = RWBit(0, _REG_MDAC, 7)

    _mdac: int = RWBits(0, 7, _REG_MDAC, 0)

    _dac_osr_lsb: int = RWBits(0, 8, _REG_DAC_OSR_LSB, 0)
    _dac_osr_msb: int = RWBits(0, 2, _REG_DAC_OSR_MSB, 0)

    @property
    def _dac_osr(self) -> int:
        return self._dac_osr_lsb | (self._dac_osr_msb << 8)

    @_dac_osr.setter
    def _dac_osr(self, value: int) -> None:
        self._dac_osr_lsb = value & 0xFF
        self._dac_osr_msb = (value >> 8) & 0x03

    _adc_osr: int = RWBits(0, 8, _REG_ADC_OSR, 0)

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, value: int) -> None:
        if value not in {8000, 11025, 22050, 44100, 48000}:
            raise ValueError("Need a valid sample rate: 8000, 11025, 22050, 44100, or 48000")

        aosr = _ADC_OSR_128
        if self._mclk is None:
            if value == 22050:
                p, r, j, d, ndac, mdac, dosr, aosr = 1, 4, 38, 0, 19, 1, 256, _ADC_OSR_256
            elif value == 44100:
                p, r, j, d, ndac, mdac, dosr = 1, 2, 38, 0, 19, 1, 128
            elif value == 48000:
                p, r, j, d, ndac, mdac, dosr = 1, 2, 34, 0, 17, 1, 128
            elif value in {8000, 11025}:
                # These PLL tuning values will cause distortion
                p, r, j, d, ndac, mdac, dosr = 1, 3, 20, 0, 5, 3, 128
        elif value == 8000:
            p, r, j, d, ndac, mdac, dosr = 1, 1, 6, 9632, 17, 1, 768
        elif value == 11025:
            p, r, j, d, ndac, mdac, dosr = 5, 1, 35, 7504, 19, 1, 512
        elif value == 22050:
            p, r, j, d, ndac, mdac, dosr, aosr = 5, 1, 35, 7504, 19, 1, 256, _ADC_OSR_256
        elif value == 44100:
            p, r, j, d, ndac, mdac, dosr = 5, 1, 35, 7504, 19, 1, 128
        elif value == 48000:
            p, r, j, d, ndac, mdac, dosr = 1, 1, 6, 9632, 17, 1, 128

        self._sample_rate = value

        # 1. Ensure DAC, ADC and PLL are powered down
        self.dac_enabled = False
        self.adc_enabled = False
        self._pll_enabled = False
        time.sleep(0.001)

        # 2. Set PLL clock scaling registers
        self._pll_p = p
        self._pll_r = r
        self._pll_j = j
        self._pll_d = d

        # 3. Set mux for PLL input clock source (PLL_CLKIN)
        self._pll_clkin = _PLL_CLKIN_BCLK if self._mclk is None else _PLL_CLKIN_MCLK

        # 4. Power up  PLL and wait briefly for PLL lock
        self._pll_enabled = True
        time.sleep(0.01)

        # 5. Set mux to route PLL output (PLL_CLK) to CODEC_CLKIN
        self._codec_clkin = _CODEC_CLKIN_PLL

        # 6. Set the data format
        self.audio_interface = AUDIO_INTERFACE_I2S
        self.bit_depth = 16

        # 7. Configure codec clock dividers for oversampling and DSP
        self._ndac = ndac
        self._ndac_enabled = True
        self._mdac = mdac
        self._mdac_enabled = True
        self._dac_osr = dosr
        self._adc_osr = aosr

    left_headphone_output_enabled: bool = RWBit(1, _REG_OUTPUT_DRIVER_POWER, 5)
    right_headphone_output_enabled: bool = RWBit(1, _REG_OUTPUT_DRIVER_POWER, 4)

    @property
    def headphone_output_enabled(self) -> bool:
        return self.left_headphone_output_enabled or self.right_headphone_output_enabled

    @headphone_output_enabled.setter
    def headphone_output_enabled(self, value: bool) -> None:
        self.left_headphone_output_enabled = value
        self.right_headphone_output_enabled = value

    left_line_output_enabled: bool = RWBit(1, _REG_OUTPUT_DRIVER_POWER, 3)
    right_line_output_enabled: bool = RWBit(1, _REG_OUTPUT_DRIVER_POWER, 2)

    @property
    def line_output_enabled(self) -> bool:
        return self.left_line_output_enabled or self.right_line_output_enabled

    @line_output_enabled.setter
    def line_output_enabled(self, value: bool) -> None:
        self.left_line_output_enabled = value
        self.right_line_output_enabled = value

    left_dac_to_left_headphone_output: bool = RWBit(1, _REG_HPL_ROUTING, 3)
    right_dac_to_right_headphone_output: bool = RWBit(1, _REG_HPL_ROUTING, 3)

    @property
    def dac_to_headphone_output(self) -> bool:
        return self.left_dac_to_left_headphone_output or self.right_dac_to_right_headphone_output

    @dac_to_headphone_output.setter
    def dac_to_headphone_output(self, value: bool) -> None:
        self.left_dac_to_left_headphone_output = value
        self.right_dac_to_right_headphone_output = value

    left_dac_to_left_line_output: bool = RWBit(1, _REG_LOL_ROUTING, 3)
    right_dac_to_right_line_output: bool = RWBit(1, _REG_LOR_ROUTING, 3)

    @property
    def dac_to_line_output(self) -> bool:
        return self.left_dac_to_left_line_output or self.right_dac_to_right_line_output

    @dac_to_line_output.setter
    def dac_to_line_output(self, value: bool) -> None:
        self.left_dac_to_left_line_output = value
        self.right_dac_to_right_line_output = value

    left_input_passthrough_enabled: bool = RWBit(1, _REG_OUTPUT_DRIVER_POWER, 1)
    right_input_passthrough_enabled: bool = RWBit(1, _REG_OUTPUT_DRIVER_POWER, 0)

    @property
    def input_passthrough_enabled(self) -> bool:
        return self.left_input_passthrough_enabled or self.right_input_passthrough_amp_enabled

    @input_passthrough_enabled.setter
    def input_passthrough_enabled(self, value: bool) -> None:
        self.left_input_passthrough_enabled = value
        self.right_input_passthrough_enabled = value

    left_input_to_left_line_output: bool = RWBit(1, _REG_LOL_ROUTING, 1)
    right_input_to_right_line_output: bool = RWBit(1, _REG_LOR_ROUTING, 1)

    @property
    def input_to_line_output(self) -> bool:
        return (
            self.left_input_to_left_line_output or self.right_input_to_right_line_output
        )

    @input_to_line_output.setter
    def input_to_line_output(self, value: bool) -> None:
        self.left_input_to_left_line_output = value
        self.right_input_to_right_line_output = value

    left_input_to_left_headphone_output: bool = RWBit(1, _REG_HPL_ROUTING, 1)
    right_input_to_right_headphone_output: bool = RWBit(1, _REG_HPR_ROUTING, 1)

    @property
    def input_to_headphone_output(self) -> bool:
        return (
            self.left_input_to_left_headphone_output
            or self.right_input_to_right_headphone_output
        )

    @input_to_headphone_output.setter
    def input_to_headphone_output(self, value: bool) -> None:
        self.left_input_to_left_headphone_output = value
        self.right_input_to_right_headphone_output = value

    left_input1_to_left_headphone_output: bool = RWBit(1, _REG_HPL_ROUTING, 2)
    right_input1_to_right_headphone_output: bool = RWBit(1, _REG_HPR_ROUTING, 2)

    @property
    def input1_to_headphone_output(self) -> bool:
        return (
            self.left_input1_to_left_headphone_output or self.right_input1_to_right_headphone_output
        )

    @input1_to_headphone_output.setter
    def input1_to_headphone_output(self, value: bool) -> None:
        self.left_input1_to_left_headphone_output = value
        self.right_input1_to_right_headphone_output = value

    left_input1_to_left_headphone_output_volume: float = VolumeBits(
        1, _REG_IN1L_TO_HPL_VOLUME, _UINT7_VOLUME_TABLE, True
    )
    right_input1_to_right_headphone_output_volume: float = VolumeBits(
        1, _REG_IN1R_TO_HPR_VOLUME, _UINT7_VOLUME_TABLE, True
    )

    @property
    def input1_to_headphone_output_volume(self) -> float:
        return self.left_input1_to_left_headphone_output_volume

    @input1_to_headphone_output_volume.setter
    def input1_to_headphone_output_volume(self, value: float) -> None:
        self.left_input1_to_left_headphone_output_volume = value
        self.right_input1_to_right_headphone_output_volume = value

    left_input_passthrough_volume: float = VolumeBits(
        1, _REG_MIXER_LEFT_VOLUME, _UINT6_VOLUME_TABLE, True
    )
    right_input_passthrough_volume: float = VolumeBits(
        1, _REG_MIXER_RIGHT_VOLUME, _UINT6_VOLUME_TABLE, True
    )

    @property
    def input_passthrough_volume(self) -> float:
        return self.left_input_passthrough_volume

    @input_passthrough_volume.setter
    def input_passthrough_volume(self, value: float) -> None:
        self.left_input_passthrough_volume = value
        self.right_input_passthrough_volume = value

    left_headphone_output_muted: bool = RWBit(1, _REG_HPL_GAIN, 6)
    right_headphone_output_muted: bool = RWBit(1, _REG_HPR_GAIN, 6)

    @property
    def headphone_output_muted(self) -> bool:
        return self.left_headphone_output_muted or self.right_headphone_output_muted

    @headphone_output_muted.setter
    def headphone_output_muted(self, value: bool) -> None:
        self.left_headphone_output_muted = value
        self.right_headphone_output_muted = value

    left_headphone_output_gain: float = RWBits(1, 6, _REG_HPL_GAIN, 0, signed=True)
    right_headphone_output_gain: float = RWBits(1, 6, _REG_HPR_GAIN, 0, signed=True)

    @property
    def headphone_output_gain(self) -> float:
        return self.left_headphone_output_gain

    @headphone_output_gain.setter
    def headphone_output_gain(self, value: float) -> None:
        self.left_headphone_output_gain = value
        self.right_headphone_output_gain = value

    left_line_output_muted: bool = RWBit(1, _REG_LOL_GAIN, 6)
    right_line_output_muted: bool = RWBit(1, _REG_LOR_GAIN, 6)

    @property
    def line_output_muted(self) -> bool:
        return self.left_line_output_muted or self.right_line_output_muted

    @line_output_muted.setter
    def line_output_muted(self, value: bool) -> None:
        self.left_line_output_muted = value
        self.right_line_output_muted = value

    left_line_output_gain: float = RWBits(1, 6, _REG_LOL_GAIN, 0, signed=True)
    right_line_output_gain: float = RWBits(1, 6, _REG_LOR_GAIN, 0, signed=True)

    @property
    def line_output_gain(self) -> float:
        return self.left_line_output_gain

    @line_output_gain.setter
    def line_output_gain(self, value: float) -> None:
        self.left_line_output_gain = value
        self.right_line_output_gain = value

    micbias_enabled: bool = RWBit(1, _REG_MICBIAS, 6)
    micbias_mode: int = RWBits(1, 2, _REG_MICBIAS, 4)
    micbias_source: bool = RWBit(1, _REG_MICBIAS, 3)

    _in1l_to_left_mic_pos: int = RWBits(1, 2, _REG_LEFT_MICPGA_POS, 6)
    _in2l_to_left_mic_pos: int = RWBits(1, 2, _REG_LEFT_MICPGA_POS, 4)
    _in3l_to_left_mic_pos: int = RWBits(1, 2, _REG_LEFT_MICPGA_POS, 2)

    _cm_to_left_mic_neg: int = RWBits(1, 2, _REG_LEFT_MICPGA_NEG, 6)
    _in2r_to_left_mic_neg: int = RWBits(1, 2, _REG_LEFT_MICPGA_NEG, 4)
    _in3r_to_left_mic_neg: int = RWBits(1, 2, _REG_LEFT_MICPGA_NEG, 2)

    _in1r_to_right_mic_pos: int = RWBits(1, 2, _REG_RIGHT_MICPGA_POS, 6)
    _in2r_to_right_mic_pos: int = RWBits(1, 2, _REG_RIGHT_MICPGA_POS, 4)
    _in3r_to_right_mic_pos: int = RWBits(1, 2, _REG_RIGHT_MICPGA_POS, 2)

    _cm_to_right_mic_neg: int = RWBits(1, 2, _REG_RIGHT_MICPGA_NEG, 6)
    _in1l_to_right_mic_neg: int = RWBits(1, 2, _REG_RIGHT_MICPGA_NEG, 4)
    _in3l_to_right_mic_neg: int = RWBits(1, 2, _REG_RIGHT_MICPGA_NEG, 2)

    _in1l_floating: bool = RWBit(1, _REG_FLOATING_INPUT, 7)
    _in1r_floating: bool = RWBit(1, _REG_FLOATING_INPUT, 6)
    _in2l_floating: bool = RWBit(1, _REG_FLOATING_INPUT, 5)
    _in2r_floating: bool = RWBit(1, _REG_FLOATING_INPUT, 4)
    _in3l_floating: bool = RWBit(1, _REG_FLOATING_INPUT, 3)
    _in3r_floating: bool = RWBit(1, _REG_FLOATING_INPUT, 2)

    def _update_floating(self) -> None:
        self._in1l_floating = (
            self._in1l_to_left_mic_pos != MIC_DISCONNECTED
            or self._in1l_to_right_mic_neg != MIC_DISCONNECTED
        )
        self._in1r_floating = self._in1r_to_right_mic_pos != MIC_DISCONNECTED
        self._in2l_floating = self._in2l_to_left_mic_pos != MIC_DISCONNECTED
        self._in2r_floating = (
            self._in2r_to_left_mic_neg != MIC_DISCONNECTED
            or self._in2r_to_right_mic_pos != MIC_DISCONNECTED
        )
        self._in3l_floating = (
            self._in3l_to_left_mic_pos != MIC_DISCONNECTED
            or self._in3l_to_right_mic_neg != MIC_DISCONNECTED
        )
        self._in3r_floating = (
            self._in3r_to_left_mic_neg != MIC_DISCONNECTED
            or self._in3r_to_right_mic_pos != MIC_DISCONNECTED
        )

    def connect_left_mic_input(
        self, input: int, impedance: int = MIC_IMPEDANCE_10K, balanced: bool = False
    ) -> None:
        if input == MIC_INPUT_1 and balanced:
            raise ValueError("Balanced IN1 input only supported on right channel")

        self._in1l_to_left_mic_pos = impedance if input == MIC_INPUT_1 else MIC_DISCONNECTED
        self._in2l_to_left_mic_pos = impedance if input == MIC_INPUT_2 else MIC_DISCONNECTED
        self._in3l_to_left_mic_pos = impedance if input == MIC_INPUT_3 else MIC_DISCONNECTED

        self._cm_to_left_mic_neg = impedance if not balanced else MIC_DISCONNECTED
        self._in2r_to_left_mic_neg = (
            impedance if input == MIC_INPUT_2 and balanced else MIC_DISCONNECTED
        )
        self._in3r_to_left_mic_neg = (
            impedance if input == MIC_INPUT_3 and balanced else MIC_DISCONNECTED
        )

        self._update_floating()

    def connect_right_mic_input(
        self, input: int, impedance: int = MIC_IMPEDANCE_10K, balanced: bool = False
    ) -> None:
        if input == MIC_INPUT_2 and balanced:
            raise ValueError("Balanced IN2 input only supported on left channel")

        self._in1r_to_right_mic_pos = impedance if input == MIC_INPUT_1 else MIC_DISCONNECTED
        self._in2r_to_right_mic_pos = impedance if input == MIC_INPUT_2 else MIC_DISCONNECTED
        self._in3r_to_right_mic_pos = impedance if input == MIC_INPUT_3 else MIC_DISCONNECTED

        self._cm_to_right_mic_neg = impedance if not balanced else MIC_DISCONNECTED
        self._in1l_to_right_mic_neg = (
            impedance if input == MIC_INPUT_1 and balanced else MIC_DISCONNECTED
        )
        self._in3l_to_right_mic_neg = (
            impedance if input == MIC_INPUT_3 and balanced else MIC_DISCONNECTED
        )

        self._update_floating()

    def connect_mic_input(self, input: int, impedance: int = MIC_IMPEDANCE_10K) -> None:
        self.connect_left_mic_input(input, impedance)
        self.connect_right_mic_input(input, impedance)

    _left_mic_gain_disabled: bool = RWBit(1, _REG_LEFT_MICPGA_GAIN, 7)
    _left_mic_gain: int = RWBits(1, 7, _REG_LEFT_MICPGA_GAIN, 0)

    @property
    def left_mic_gain(self) -> float:
        return min(max(self._left_mic_gain, 0), 95) / 2 if not self._left_mic_gain_disabled else 0.0

    @left_mic_gain.setter
    def left_mic_gain(self, value: float) -> None:
        value = min(max(round(value * 2), 0), 95)
        self._left_mic_gain_disabled = value <= 0
        self._left_mic_gain = value

    _right_mic_gain_disabled: bool = RWBit(1, _REG_RIGHT_MICPGA_GAIN, 7)
    _right_mic_gain: int = RWBits(1, 7, _REG_RIGHT_MICPGA_GAIN, 0)

    @property
    def right_mic_gain(self) -> float:
        return (
            min(max(self._right_mic_gain, 0), 95) / 2 if not self._right_mic_gain_disabled else 0.0
        )

    @right_mic_gain.setter
    def right_mic_gain(self, value: float) -> None:
        value = min(max(round(value * 2), 0), 95)
        self._right_mic_gain_disabled = value <= 0
        self._right_mic_gain = value

    @property
    def mic_gain(self) -> float:
        return self.left_mic_gain

    @mic_gain.setter
    def mic_gain(self, value: float) -> None:
        self.left_mic_gain = value
        self.right_mic_gain = value

    left_adc_enabled: bool = RWBit(0, _REG_ADC_CHANNEL_1, 7)
    right_adc_enabled: bool = RWBit(0, _REG_ADC_CHANNEL_1, 6)

    @property
    def adc_enabled(self) -> bool:
        return self.left_adc_enabled or self.right_adc_enabled

    @adc_enabled.setter
    def adc_enabled(self, value: bool) -> None:
        self.left_adc_enabled = value
        self.right_adc_enabled = value

    left_adc_muted: bool = RWBit(0, _REG_ADC_CHANNEL_2, 7)
    right_adc_muted: bool = RWBit(0, _REG_ADC_CHANNEL_2, 3)

    @property
    def adc_muted(self) -> bool:
        return self.left_adc_muted or self.right_adc_muted

    @adc_muted.setter
    def adc_muted(self, value: bool) -> None:
        self.left_adc_muted = value
        self.right_adc_muted = value

    _left_adc_volume: int = RWBits(0, 7, _REG_LEFT_ADC_VOLUME, 0, signed=True)

    @property
    def left_adc_volume(self) -> float:
        return self._left_adc_volume / 2

    @left_adc_volume.setter
    def left_adc_volume(self, value: float) -> None:
        self._left_adc_volume = min(max(round(value * 2), -24), 40)

    _right_adc_volume: int = RWBits(0, 7, _REG_RIGHT_ADC_VOLUME, 0, signed=True)

    @property
    def right_adc_volume(self) -> float:
        return self._right_adc_volume / 2

    @right_adc_volume.setter
    def right_adc_volume(self, value: float) -> None:
        self._right_adc_volume = min(max(round(value * 2), -24), 40)

    @property
    def adc_volume(self) -> float:
        return self.left_adc_volume

    @adc_volume.setter
    def adc_volume(self, value: float) -> None:
        self.left_adc_volume = value
        self.right_adc_volume = value
