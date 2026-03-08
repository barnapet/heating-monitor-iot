import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
import urllib.error

# Útvonal beállítása a fő mappához
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from channels.discord import DiscordNotifier
from channels.telegram import TelegramNotifier

class TestDiscordNotifier(unittest.TestCase):

    @patch('urllib.request.urlopen')
    def test_discord_send_success(self, mock_urlopen):
        """
        Forgatókönyv: A DiscordNotifier-nek küldünk egy üzenetet, az API sikeresen válaszol.
        Elvárás: A kód helyesen rakja össze a HTTP kérést (URL, Header, JSON body).
        """
        # --- 1. ARRANGE ---
        # Létrehozunk egy kamu választ, amit a 'urlopen' fog visszaadni (pl. HTTP 200 OK)
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200 
        mock_response.read.return_value = b"ok"

        mock_response.__enter__.return_value = mock_response

        mock_urlopen.return_value = mock_response

        # Példányosítjuk a valódi Discord osztályunkat egy kamu webhook URL-lel
        notifier = DiscordNotifier(webhook_url="https://fake-discord.com/api/webhook")
        test_message = "🔥 Teszt riasztás 🔥"

        # --- 2. ACT ---
        notifier.send(test_message)

        # --- 3. ASSERT ---
        # 1. Meghívta egyáltalán az internetet?
        mock_urlopen.assert_called_once()

        # 2. Megszerezzük magát a Request objektumot, amit a kódunk megpróbált elküldeni!
        # A call_args[0][0] azt jelenti: az első hívás, első paramétere.
        request_obj = mock_urlopen.call_args[0][0]

        # 3. Validáljuk, hogy jól rakta-e össze a hálózati kérést!
        self.assertEqual(request_obj.full_url, "https://fake-discord.com/api/webhook")
        self.assertEqual(request_obj.get_method(), "POST")
        
        # 4. Validáljuk, hogy a JSON body olyan-e, amilyet a Discord elvár: {"content": "üzenet"}
        payload = json.loads(request_obj.data.decode('utf-8'))
        self.assertEqual(payload, {"content": test_message, "username": "Boiler Monitor"})

    @patch('urllib.request.urlopen')
    def test_discord_send_handles_network_error(self, mock_urlopen):
        """
        Forgatókönyv: A Discord szerver nem elérhető (404-es hiba vagy Timeout).
        Elvárás: A send() metódus HTTPError-t vagy URLError-t dob, amit a mi kódunk továbbenged.
        """
        # --- 1. ARRANGE ---
        # Azt hazudjuk, hogy az internet megszakadt (urllib hiba)
        mock_urlopen.side_effect = urllib.error.URLError("Network unreachable")
        
        notifier = DiscordNotifier(webhook_url="https://fake-discord.com/api/webhook")

        # --- 2. ACT & 3. ASSERT ---
        # Mivel a base.py-ban lévő send() elkapja, logolja, majd ÚJRADOBJA (raise) a hibát,
        # itt elvárjuk, hogy kivétel keletkezzen!
        with self.assertRaises(Exception) as context:
            notifier.send("Hiba teszt")
            
        self.assertIn("Network unreachable", str(context.exception))

class TestTelegramNotifier(unittest.TestCase):

    @patch('urllib.request.urlopen')
    def test_telegram_send_success(self, mock_urlopen):
        """
        Forgatókönyv: A Telegram API sikeresen válaszol (HTTP 200).
        Elvárás: Jó URL, helyes POST method és megfelelő JSON test jön létre.
        """
        # --- ARRANGE ---
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b'{"ok": true}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        notifier = TelegramNotifier(token="bot12345", chat_id="chat987")
        test_message = "Működik a Telegram!"

        # --- ACT ---
        notifier.send(test_message)

        # --- ASSERT ---
        mock_urlopen.assert_called_once()
        request_obj = mock_urlopen.call_args[0][0]

        # Ellenőrizzük az egyedi Telegram URL generálást!
        self.assertEqual(request_obj.full_url, "https://api.telegram.org/botbot12345/sendMessage")
        self.assertEqual(request_obj.get_method(), "POST")
        
        # A Telegram 'chat_id' és 'text' kulcsokat vár
        payload = json.loads(request_obj.data.decode('utf-8'))
        self.assertEqual(payload, {"chat_id": "chat987", 
                                   "text": test_message, 
                                   "parse_mode": "Markdown"})

    @patch('urllib.request.urlopen')
    def test_http_error_status_raises_exception(self, mock_urlopen):
        """
        Forgatókönyv: A hívás elmegy, de a szerver HTTP 404 (vagy 500) hibát ad.
        Elvárás: A base.py 24. sora (a státuszkód ellenőrzés) kivételt dob.
        """
        # --- ARRANGE ---
        mock_response = MagicMock()
        # ITT A LÉNYEG: 200 helyett 404-es hibát szimulálunk!
        mock_response.getcode.return_value = 404 
        mock_response.read.return_value = b"Not Found"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        notifier = TelegramNotifier(token="bot12345", chat_id="chat987")

        # --- ACT & ASSERT ---
        with self.assertRaises(Exception) as context:
            notifier.send("Rossz végpont")

        self.assertIn("HTTP Error: 404", str(context.exception))