# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2026 Cooper Dalrymple
#
# SPDX-License-Identifier: Unlicense

import board

import relic_tlv320aic3204

# Initialize codec
codec = relic_tlv320aic3204.TLV320AIC3204(
    i2c=board.STEMMA_I2C(),
    rst=board.GP16,
)  # defaults to 16 bit, 44.1khz sample rate

# Direct Passthrough of INPUT1 to Headphones
# codec.input1_to_headphone_output = True
# codec.input1_to_headphone_output_volume = 0.0  # dB

# Enable mic input and connect to desired source
codec.connect_input(relic_tlv320aic3204.INPUT_1)
codec.input_gain = 0.0  # dB

# Setup Passthrough Input Mixer
codec.input_passthrough_enabled = True
codec.input_passthrough_volume = 0.0  # dB

# Line Output
codec.input_to_line_output = True
codec.line_output_enabled = True
codec.line_output_muted = False

# Headphone Output
# codec.input_to_headphone_output = True
# codec.headphone_output_enabled = True
# codec.headphone_output_muted = False
