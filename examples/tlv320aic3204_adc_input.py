# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2026 Cooper Dalrymple
#
# SPDX-License-Identifier: Unlicense

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
    data_in=board.GP21,
    sample_rate=codec.sample_rate,
    channel_count=1,
)

# Connect IN1L to Left MICPGA and IN1R to Right MICPGA
codec.connect_mic_input(relic_tlv320aic3204.MIC_INPUT_1, relic_tlv320aic3204.MIC_IMPEDANCE_20K)
codec.mic_gain = 6.0  # dB


# Setup ADC Input
codec.dac_enabled = True  # BUG: DAC must be enabled for ADC functionality
codec.adc_volume = 0.0  # dB
codec.adc_enabled = True
codec.adc_muted = False

while True:
    print(np.max(np.array(i2s.read(block=True), dtype=np.int16)))
