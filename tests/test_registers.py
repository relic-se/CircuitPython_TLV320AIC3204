# SPDX-FileCopyrightText: Copyright (c) 2026 Cooper Dalrymple
#
# SPDX-License-Identifier: MIT

"""Tests of what the driver writes to the registers of the codec. They run on a computer with
`pytest` from the root of the repository, with the real ``adafruit_register`` library and a
stand-in for the I2C bus that keeps the registers of each page."""

import os
import sys
import types

import pytest


class FakeCodec:
    """Stands in for ``I2CDevice``: register 0 selects the page of the other registers."""

    def __init__(self, i2c=None, address=None):
        self.page = 0
        self.registers = {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def write(self, buffer, *, start=0, end=None):
        data = bytes(buffer[start:end])
        for offset, value in enumerate(data[1:]):
            register = data[0] + offset
            if register == 0:
                self.page = value
            elif (self.page, register) == (0, 1) and value & 1:
                self.registers.clear()  # software reset
            else:
                self.registers[self.page, register] = value

    def write_then_readinto(  # noqa: PLR0913
        self, out_buffer, in_buffer, *, out_start=0, out_end=None, in_start=0, in_end=None
    ):
        register = out_buffer[out_start]
        if in_end is None:
            in_end = len(in_buffer)
        for offset, index in enumerate(range(in_start, in_end)):
            if register + offset == 0:
                in_buffer[index] = self.page
            else:
                in_buffer[index] = self.registers.get((self.page, register + offset), 0)


def _module(name, **attributes):
    module = types.ModuleType(name)
    module.__dict__.update(attributes)
    sys.modules[name] = module


# The hardware modules of CircuitPython that the driver imports
_module("digitalio", DigitalInOut=object, Direction=types.SimpleNamespace(OUTPUT=1))
_module("microcontroller", Pin=object)
_module("pwmio", PWMOut=object)
_module("busio", I2C=object)
_module("micropython", const=lambda value: value)
_module("adafruit_bus_device")
_module("adafruit_bus_device.i2c_device", I2CDevice=FakeCodec)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from relic_tlv320aic3204 import TLV320AIC3204  # noqa: E402

PAGE_0 = 0
PAGE_1 = 1
LEFT_ADC_VOLUME = 0x53
HPL_GAIN = 0x10
HPR_GAIN = 0x11
LOL_GAIN = 0x12
LOR_GAIN = 0x13
MUTE = 0x40


@pytest.fixture
def codec():
    return TLV320AIC3204(None)


def register(codec, page, address):
    return codec.i2c_device.registers.get((page, address), 0)


@pytest.mark.parametrize(
    ("name", "address"),
    (
        ("left_line_output", LOL_GAIN),
        ("right_line_output", LOR_GAIN),
        ("left_headphone_output", HPL_GAIN),
        ("right_headphone_output", HPR_GAIN),
    ),
)
@pytest.mark.parametrize("gain", (-6, -1, 0, 3, 29))
def test_output_gain(codec, name, address, gain):
    """The gain is the lower six bits of the register as a signed value. Bit 6 mutes the output."""
    setattr(codec, name + "_muted", False)
    setattr(codec, name + "_gain", gain)
    assert register(codec, PAGE_1, address) == gain & 0x3F
    assert getattr(codec, name + "_gain") == gain
    assert getattr(codec, name + "_muted") is False


@pytest.mark.parametrize("name", ("left_line_output", "left_headphone_output"))
def test_output_gain_keeps_mute(codec, name):
    setattr(codec, name + "_muted", True)
    setattr(codec, name + "_gain", -6)
    assert getattr(codec, name + "_muted") is True
    setattr(codec, name + "_gain", 6)
    assert getattr(codec, name + "_muted") is True
    setattr(codec, name + "_muted", False)
    assert getattr(codec, name + "_gain") == 6


def test_output_gain_after_negative_gain(codec):
    codec.left_line_output_muted = False
    codec.left_line_output_gain = -6
    codec.left_line_output_gain = 3
    assert register(codec, PAGE_1, LOL_GAIN) == 3
    assert codec.left_line_output_muted is False


@pytest.mark.parametrize("volume", (-12.0, -0.5, 0.0, 20.0))
def test_adc_volume(codec, volume):
    """The volume is the lower seven bits of the register in steps of 0.5 dB. Bit 7 is reserved."""
    codec.left_adc_volume = volume
    assert register(codec, PAGE_0, LEFT_ADC_VOLUME) == round(volume * 2) & 0x7F
    assert codec.left_adc_volume == volume
