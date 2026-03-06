import sys
from unittest.mock import MagicMock

# This is the senior‑level trick:
# Before any module attempts to import real hardware libraries,
# we inject mock versions into sys.modules.
# This ensures the code runs on Windows or CI environments
# without requiring actual Raspberry Pi hardware.

# 1. Mock the RPi.GPIO module
mock_gpio = MagicMock()
sys.modules["RPi"] = MagicMock()
sys.modules["RPi.GPIO"] = mock_gpio

# 2. Mock the temperature sensor library (w1thermsensor)
# If you use a different sensor library (e.g., Adafruit_DHT),
# mock that one here instead.
mock_w1 = MagicMock()
sys.modules["w1thermsensor"] = mock_w1

# 3. Mock the AWS IoT SDK to prevent real network connections
sys.modules["awscrt"] = MagicMock()
sys.modules["awsiot"] = MagicMock()
