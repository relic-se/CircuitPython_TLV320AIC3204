# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2026 Cooper Dalrymple
#
# SPDX-License-Identifier: Unlicense

import array
import math

import board
import pio_i2s
import ulab.numpy as np

import relic_tlv320aic3204

# Initialize codec
codec = relic_tlv320aic3204.TLV320AIC3204(
    i2c=board.STEMMA_I2C(),
    mclk=board.GP17,
    rst=board.GP16,
)  # defaults to 16 bit, 44.1khz sample rate
i2s = pio_i2s.I2S(
    bit_clock=board.GP18,
    word_select=board.GP19,
    data_out=board.GP20,
    data_in=board.GP21,
    sample_rate=codec.sample_rate,
    channel_count=1,
)

# Setup DAC Output
codec.dac_volume = 0.0  # dB
codec.dac_enabled = True
codec.dac_muted = False

# Line Output
codec.dac_to_line_output = True
codec.line_output_enabled = True
codec.line_output_muted = False

# Connect IN1L to Left MICPGA and IN1R to Right MICPGA
codec.connect_input(relic_tlv320aic3204.INPUT_1, relic_tlv320aic3204.INPUT_IMPEDANCE_20K)
codec.input_gain = 6.0  # dB

# Setup ADC Input
codec.adc_volume = 0.0  # dB
codec.adc_enabled = True
codec.adc_muted = False

# Play sine wave
length = codec.sample_rate // 440
sine_wave = array.array(i2s.buffer_format, [0] * i2s.buffer_size)
for i in range(i2s.buffer_size):
    sine_wave[i] = min(max(int(math.sin(math.pi * 2 * i / length) * (2**15)), -32768), 32767)
i2s.write(sine_wave, loop=True)

while True:
    print(np.max(np.array(i2s.read(block=True), dtype=np.int16)))
