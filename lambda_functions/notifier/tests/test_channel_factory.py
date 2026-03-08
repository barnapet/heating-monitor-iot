import unittest
from unittest.mock import patch
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import channel_factory
from channels.telegram import TelegramNotifier
from channels.discord import DiscordNotifier

class TestChannelFactory(unittest.TestCase):

    def setUp(self):
        # A valós osztályokat használjuk, de az SSM kulcsokat elmaszkoljuk!
        self.env_patcher = patch.dict(os.environ, {
            "SSM_KEY_TOKEN": "/test/token",
            "SSM_KEY_CHAT_ID": "/test/chat_id",
            "SSM_KEY_DISCORD_WEBHOOK": "/test/discord"
        })
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    @patch('channel_factory.ssm')
    def test_factory_builds_all_configured_channels_successfully(self, mock_ssm):
        """Forgatókönyv: Minden SSM titok megvan az éles Registry-hez."""
        # Mindig érvényes, https-sel kezdődő értéket adunk vissza
        mock_ssm.get_parameter.return_value = {'Parameter': {'Value': 'https://valid_secret'}}

        channels = channel_factory.get_active_channels()
        channel_types = [type(c) for c in channels]

        # PROFI ELLENŐRZÉS: Nem a lista hosszát nézzük (hogy ne törjön el, ha jön a Slack),
        # hanem azt, hogy a kötelező alapcsatornák sikeresen legyártódtak-e!
        self.assertIn(TelegramNotifier, channel_types, "TelegramNotifier is missing from active channels!")
        self.assertIn(DiscordNotifier, channel_types, "DiscordNotifier is missing from active channels!")

        # Validáljuk az éles kábelezést (hogy jó paramétert kapott-e a Discord)
        discord_instance = next(c for c in channels if isinstance(c, DiscordNotifier))
        self.assertEqual(discord_instance.webhook_url, 'https://valid_secret')

    @patch('channel_factory.ssm')
    def test_factory_skips_discord_when_webhook_is_not_https(self, mock_ssm):
        """Forgatókönyv: A Discord URL megvan az SSM-ben, de nem 'https'-sel kezdődik."""
        def ssm_side_effect(Name, WithDecryption):
            if "discord" in Name:
                # Szimulálunk egy hibás, titkosítatlan URL-t a konfigurációban
                return {'Parameter': {'Value': 'http://insecure_url.com'}}
            return {'Parameter': {'Value': 'https://valid_secret'}}
        mock_ssm.get_parameter.side_effect = ssm_side_effect

        channels = channel_factory.get_active_channels()
        channel_types = [type(c) for c in channels]

        # Mivel a Discord URL hibás, a Gyárnak ki kell hagynia!
        self.assertIn(TelegramNotifier, channel_types)
        self.assertNotIn(DiscordNotifier, channel_types)

    @patch('channel_factory.ssm')
    def test_factory_skips_discord_when_webhook_missing(self, mock_ssm):
        """Forgatókönyv: A Discord URL-je hiányzik az SSM-ből."""
        def ssm_side_effect(Name, WithDecryption):
            if "discord" in Name:
                raise Exception("ParameterNotFound")
            return {'Parameter': {'Value': 'https://valid_secret'}}
        mock_ssm.get_parameter.side_effect = ssm_side_effect

        channels = channel_factory.get_active_channels()
        channel_types = [type(c) for c in channels]

        # A Telegramnak benne kell lennie, de a Discordnak NEM!
        self.assertIn(TelegramNotifier, channel_types)
        self.assertNotIn(DiscordNotifier, channel_types)

    @patch('channel_factory.ssm')
    def test_factory_skips_telegram_when_partial_secrets_missing(self, mock_ssm):
        """Forgatókönyv: A Discord megvan, a Telegram token megvan, de a chat_id hiányzik."""
        def ssm_side_effect(Name, WithDecryption):
            if "chat_id" in Name:
                raise Exception("ParameterNotFound")
            return {'Parameter': {'Value': 'https://valid_secret'}}
        mock_ssm.get_parameter.side_effect = ssm_side_effect

        channels = channel_factory.get_active_channels()
        channel_types = [type(c) for c in channels]

        # A Discordnak benne kell lennie, de a Telegramnak NEM!
        self.assertIn(DiscordNotifier, channel_types)
        self.assertNotIn(TelegramNotifier, channel_types)

    @patch.dict(os.environ, {}, clear=True) # FIGYELEM: clear=True töröl minden környezeti változót!
    @patch('channel_factory.ssm')
    def test_factory_returns_empty_when_env_vars_are_missing(self, mock_ssm):
        """
        Forgatókönyv: A környezeti változók (SSM_KEY_...) egyáltalán nincsenek beállítva a Lambdában.
        Elvárás: A get_secret függvény az 'if not path' ágon azonnal None-t ad vissza, 
                 így a Gyár kihagyja a csatornákat, és üres listát kapunk.
        """
        # ACT
        channels = channel_factory.get_active_channels()

        # ASSERT
        self.assertEqual(len(channels), 0)
        self.assertEqual(channels, [])
        # Az SSM-et meg sem szabadott volna hívnia a kódnak, hiszen már a path sem volt meg!
        mock_ssm.get_parameter.assert_not_called()

    @patch('channel_factory.ssm')
    def test_factory_returns_empty_when_all_missing(self, mock_ssm):
        """Forgatókönyv: Semmi nincs beállítva az AWS-ben."""
        mock_ssm.get_parameter.side_effect = Exception("ParameterNotFound")

        channels = channel_factory.get_active_channels()

        self.assertEqual(len(channels), 0)
        self.assertEqual(channels, [])