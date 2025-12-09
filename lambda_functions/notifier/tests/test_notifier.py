import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json

# --- Path injection ---
# Add the parent directory (notifier/) to the Python path
# so that index.py can be imported during testing.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Import the module under test ---
# Note: If the 'channels' package is missing in CI/CD environments,
# this import may fail. We assume the full repo is available.
import index


class TestNotifierLambda(unittest.TestCase):

    def setUp(self):
        """
        Before each test, patch environment variables so the Lambda
        behaves as if valid SSM parameter names were provided.
        """
        self.env_patcher = patch.dict(os.environ, {
            "SSM_KEY_TOKEN": "/test/token",
            "SSM_KEY_CHAT_ID": "/test/chat_id",
            "SSM_KEY_DISCORD_WEBHOOK": "/test/discord"
        })
        self.env_patcher.start()

    def tearDown(self):
        """
        Restore environment variables after each test.
        """
        self.env_patcher.stop()

    @patch('index.ssm')
    @patch('index.TelegramNotifier')
    @patch('index.DiscordNotifier')
    def test_inactive_status_sends_alert_to_both_channels(self, MockDiscord, MockTelegram, mock_ssm):
        """
        Scenario:
            An 'INACTIVE' status event arrives and SSM successfully returns
            all required secrets for both Telegram and Discord.

        Expectation:
            Both Telegram and Discord notifiers should send an alert message.
        """

        # 1. Configure the SSM mock
        # FIX: Return a value starting with 'https://' so that Discord webhook validation passes.
        def get_parameter_side_effect(Name, WithDecryption):
            return {'Parameter': {'Value': 'https://secret_value_123'}}

        mock_ssm.get_parameter.side_effect = get_parameter_side_effect

        # Both notifier mocks should return True when .send() is called
        MockTelegram.return_value.send.return_value = True
        MockDiscord.return_value.send.return_value = True

        # 2. Define the incoming Lambda event
        event = {"status": "INACTIVE", "device_id": "test-device-01"}

        # 3. Execute the Lambda handler
        response = index.lambda_handler(event, None)

        # 4. Assertions
        self.assertEqual(response['statusCode'], 200)
        self.assertIn("2/2 channels", response['body'])

        # Verify that TelegramNotifier received the correct secrets
        # FIX: Expected values must also start with 'https://'
        MockTelegram.assert_called_with(
            token='https://secret_value_123',
            chat_id='https://secret_value_123'
        )


    @patch('index.ssm')
    def test_missing_secrets_logs_warning_and_skips_channel(self, mock_ssm):
        """
        Scenario:
            SSM returns a valid token for Telegram but raises an exception
            when attempting to fetch the Discord webhook.

        Expectation:
            get_active_channels() should return only the Telegram notifier,
            and the system should not crash.
        """

        # SSM behavior:
        # - Telegram parameters succeed
        # - Discord parameter raises an exception
        def side_effect(Name, WithDecryption):
            if "discord" in Name:
                raise Exception("ParameterNotFound")
            return {'Parameter': {'Value': 'valid_token'}}

        mock_ssm.get_parameter.side_effect = side_effect

        # Test get_active_channels() in isolation (white-box test)
        with patch('index.TelegramNotifier') as MockTelegram:
            channels = index.get_active_channels()

            # Only Telegram should be active
            self.assertEqual(len(channels), 1)
            self.assertIsInstance(channels[0], MagicMock)  # The mocked Telegram instance
