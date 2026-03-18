Introduction
============


.. image:: https://readthedocs.org/projects/circuitpython-tlv320aic3204/badge/?version=latest
    :target: https://circuitpython-tlv320aic3204.readthedocs.io/
    :alt: Documentation Status



.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/relic-se/CircuitPython_TLV320AIC3204/workflows/Build%20CI/badge.svg
    :target: https://github.com/relic-se/CircuitPython_TLV320AIC3204/actions
    :alt: Build Status


.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

Driver library for the TLV320AIC3204 audio codec


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_
* `Register <https://github.com/adafruit/Adafruit_CircuitPython_Register>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing from PyPI
=====================
On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/circuitpython-tlv320aic3204/>`_.
To install for current user:

.. code-block:: shell

    pip3 install circuitpython-tlv320aic3204

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install circuitpython-tlv320aic3204

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install circuitpython-tlv320aic3204

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install tlv320aic3204

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python

    import audiobusio
    import board

    import relic_tlv320aic3204

    codec = relic_tlv320aic3204.TLV320AIC3204(board.I2C())  # defaults to 16 bit, 44.1khz

    # Enable DAC output
    codec.dac_enabled = True
    codec.dac_volume = -20  # dB
    codec.dac_muted = False

    # Enable Headphone Output
    codec.dac_to_headphone_output = True
    codec.headphone_output_enabled = True
    codec.headphone_output_muted = False

    audio = audiobusio.I2SOut(board.I2S_BCLK, board.I2S_WS, board.I2S_DIN)

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://circuitpython-tlv320aic3204.readthedocs.io/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/relic-se/CircuitPython_TLV320AIC3204/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
