# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2026 Cooper Dalrymple
#
# SPDX-License-Identifier: Unlicense

import audiobusio
import board
import synthio
import time

from relic_tlv320aic3204 import TLV320AIC3204

# Initialize codec
codec = TLV320AIC3204(
    i2c=board.STEMMA_I2C(), mclk=board.GP17, rst=board.GP16
)  # defaults to 16 bit, 44.1khz sample rate
audio = audiobusio.I2SOut(board.GP18, board.GP19, board.GP20)

# Setup DAC Output
codec.dac_volume = 0.0  # dB
codec.dac_enabled = True
codec.dac_muted = False

# Line Output
codec.dac_to_line_output = True
codec.line_output_enabled = True
codec.line_output_muted = False

# Headphone Output
# codec.dac_to_headphone_output = True
# codec.headphone_output_enabled = True
# codec.headphone_output_muted = False

# Setup synthesizer
synth = synthio.Synthesizer(
    sample_rate=codec.sample_rate
)
audio.play(synth)

# Setup DAC Biquad Filter
# (n0, n1, n2, d0, d1, d2)
# Type=Low-pass, Hz=16000, Q=0.7, dB=0, SR=44100
biquad_pass = (0.535241, 1.070481, 0.535241, 1, 0.844146, 0.296817)
# Type=Low-pass, Hz=2000, Q=2, dB=0, SR=44100
biquad_lpf = (0.018838, 0.037677, 0.018838, 1, -1.793320, 0.868674)

def pulse(times: int = 3, rate: float = 1.0) -> None:
    for i in range(times):
        synth.press(60)
        time.sleep(rate / 2)
        synth.release_all()
        time.sleep(rate / 2)

while True:
    codec.dac_biquad_a = biquad_pass
    codec.dac_adaptive_filter_set = True
    pulse()

    codec.dac_biquad_a = biquad_lpf
    codec.dac_adaptive_filter_set = True
    pulse()
