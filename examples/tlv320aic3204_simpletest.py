# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2026 Cooper Dalrymple
#
# SPDX-License-Identifier: Unlicense

import array
import math
import time

import audiobusio
import audiocore
import board

from relic_tlv320aic3204 import TLV320AIC3204

# Initialize codec
codec = TLV320AIC3204(board.STEMMA_I2C(), board.GP17, board.GP16)  # defaults to 16 bit, 44.1khz sample rate
audio = audiobusio.I2SOut(board.GP18, board.GP19, board.GP20)

# Setup DAC Output
codec.dac_volume = 0.0  # dB
codec.dac_muted = False

# Line Output
codec.dac_to_line_output = True
codec.line_output_enabled = True
codec.line_output_muted = False

# Headphone Output
# codec.dac_to_headphone_output = True
# codec.headphone_output_enabled = True
# codec.headphone_output_muted = False

# Generate one period of sine wave
length = codec.sample_rate // 440
sine_wave = array.array("H", [0] * length)
for i in range(length):
    sine_wave[i] = min(
        max(int(math.sin(math.pi * 2 * i / length) * (2**15) + 2**15), -65536), 65535
    )
sine_wave = audiocore.RawSample(sine_wave, sample_rate=codec.sample_rate)

while True:
    audio.play(sine_wave, loop=True)
    time.sleep(0.5)
    audio.stop()
    time.sleep(0.5)
