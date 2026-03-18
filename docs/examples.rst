Simple test
------------

Ensure your device works with this simple test. Plays a 440hz sine wave at 16-bit, 44.1khz through the line output.

.. literalinclude:: ../examples/tlv320aic3204_simpletest.py
    :caption: examples/tlv320aic3204_simpletest.py
    :linenos:

Analog Passthrough
------------------

Utilize the input mixer to pass the analog signal at IN1L and IN1R through to either the line output or headphone output. Also demonstrates how to use the dedicated input 1 passthrough to headphones.

.. literalinclude:: ../examples/tlv320aic3204_simpletest.py
    :caption: examples/tlv320aic3204_simpletest.py
    :linenos:

ADC Input
---------

With the help of the `PIO I2S library <https://circuitpython-pio-i2s.readthedocs.io/en/latest/>`_, read I2S data from the single-ended line level input on IN1L.

.. literalinclude:: ../examples/tlv320aic3204_simpletest.py
    :caption: examples/tlv320aic3204_simpletest.py
    :linenos:

Bi-directional I2S
------------------

Utilize the DAC and ADC simultaneously with the help of the `PIO I2S library <https://circuitpython-pio-i2s.readthedocs.io/en/latest/>`_. Plays a 440hz sine wave at 16-bit, 44.1khz through the line output. Connect the line output to IN1L to test the ADC.

.. literalinclude:: ../examples/tlv320aic3204_simpletest.py
    :caption: examples/tlv320aic3204_simpletest.py
    :linenos:
