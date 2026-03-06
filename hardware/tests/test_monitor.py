import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock, mock_open

# --- PATH SETUP ---
# Ensure we can import the 'src' module from 'hardware'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the module to be tested
# Note: Since we have conftest.py, RPi.GPIO is already mocked at this stage.
from src import monitor

class TestHeatingMonitor(unittest.TestCase):
    
    def setUp(self):
        """
        Setup runs before every test method.
        We prepare common mocks here to avoid repetition.
        """
        # 1. Mock the configuration file content
        self.mock_config_content = json.dumps({
            "endpoint": "test-endpoint.iot.us-east-1.amazonaws.com"
        })

    @patch('src.monitor.mqtt_connection_builder') # Mock AWS IoT Builder
    @patch('builtins.open', new_callable=mock_open) # Mock file opening
    @patch('os.path.exists') # Mock file existence check
    def test_initialization_loads_config(self, mock_exists, mock_file, mock_mqtt_builder):
        """
        Test: The class should correctly load the endpoint from iot_config.json
        and attempt to establish an MQTT connection.
        """
        # Setup mocks
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = self.mock_config_content

        # Execute
        device = monitor.HeatingMonitor()

        # Assert
        self.assertEqual(device.endpoint, "test-endpoint.iot.us-east-1.amazonaws.com")
        # Verify that MQTT connection builder was called with the endpoint
        _, kwargs = mock_mqtt_builder.mtls_from_path.call_args
        self.assertEqual(kwargs['endpoint'], "test-endpoint.iot.us-east-1.amazonaws.com")

    @patch('src.monitor.GPIO')
    @patch('src.monitor.mqtt_connection_builder')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists', return_value=True)
    def test_gpio_active_logic(self, mock_exists, mock_file, mock_builder, mock_gpio):
        """
        Test: When GPIO input is LOW (Ground), the status should be 'ACTIVE'.
        (Usually pumps are active-low or rely on specific wiring).
        """
        mock_file.return_value.read.return_value = self.mock_config_content
        
        # Instantiate the monitor
        device = monitor.HeatingMonitor()

        # SIMULATE HARDWARE: GPIO.input returns LOW (0)
        mock_gpio.LOW = 0
        mock_gpio.input.return_value = 0 
        
        # Force the IS_RASPBERRY_PI flag to True for this test to ensure we test the GPIO logic
        monitor.IS_RASPBERRY_PI = True 

        # Execute
        status = device.get_pump_status()

        # Assert
        self.assertEqual(status, "ACTIVE", "GPIO LOW should translate to ACTIVE status")

    @patch('src.monitor.GPIO')
    @patch('src.monitor.mqtt_connection_builder')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists', return_value=True)
    def test_gpio_inactive_logic(self, mock_exists, mock_file, mock_builder, mock_gpio):
        """
        Test: When GPIO input is HIGH (1), the status should be 'INACTIVE'.
        """
        mock_file.return_value.read.return_value = self.mock_config_content
        device = monitor.HeatingMonitor()

        # SIMULATE HARDWARE: GPIO.input returns HIGH (1)
        mock_gpio.LOW = 0
        mock_gpio.input.return_value = 1 
        monitor.IS_RASPBERRY_PI = True 

        # Execute
        status = device.get_pump_status()

        # Assert
        self.assertEqual(status, "INACTIVE", "GPIO HIGH should translate to INACTIVE status")

    @patch('src.monitor.mqtt_connection_builder')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists', return_value=True)
    def test_publish_payload_structure(self, mock_exists, mock_file, mock_builder):
        """
        DATA CONTRACT TEST:
        Verifies that the JSON payload sent to AWS IoT Core matches the expected schema.
        This is critical for the Cloud side (Phase 4).
        """
        mock_file.return_value.read.return_value = self.mock_config_content
        device = monitor.HeatingMonitor()
        
        # Create a Mock for the MQTT connection object
        mock_connection = mock_builder.mtls_from_path.return_value
        
        # Execute: Publish a status change
        device.publish_status("ACTIVE", reason="event_change")

        # Capture the arguments passed to .publish()
        # call_args[1] contains the keyword arguments (topic, payload, qos)
        call_args = mock_connection.publish.call_args[1]
        sent_payload = json.loads(call_args['payload'])

        # Assertions (Data Contract Verification)
        self.assertIn("device_id", sent_payload)
        self.assertIn("timestamp", sent_payload)
        self.assertEqual(sent_payload["status"], "ACTIVE")
        self.assertEqual(sent_payload["sensor_voltage"], 1) # ACTIVE should be 1
        self.assertEqual(sent_payload["metadata"]["reason"], "event_change")
        self.assertEqual(sent_payload["metadata"]["location"], "Boiler Room")

    @patch('src.monitor.mqtt_connection_builder')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists', return_value=True)
    def test_heartbeat_payload_modification(self, mock_exists, mock_file, mock_builder):
        """
        Test: When sending a heartbeat, the display status should change to 'HEARTBEAT_OK',
        but the 'real_state' should remain preserved.
        """
        mock_file.return_value.read.return_value = self.mock_config_content
        device = monitor.HeatingMonitor()
        mock_connection = mock_builder.mtls_from_path.return_value

        # Execute: Publish a heartbeat while the pump is actually INACTIVE
        device.publish_status("INACTIVE", reason="heartbeat")

        # Decode payload
        call_args = mock_connection.publish.call_args[1]
        sent_payload = json.loads(call_args['payload'])

        # Assert
        self.assertEqual(sent_payload["status"], "HEARTBEAT_OK") # Display status
        self.assertEqual(sent_payload["real_state"], "INACTIVE") # Real status preserved
        self.assertEqual(sent_payload["metadata"]["reason"], "heartbeat")

if __name__ == '__main__':
    unittest.main()