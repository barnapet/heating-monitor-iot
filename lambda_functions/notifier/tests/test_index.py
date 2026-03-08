import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json

# --- Útvonal beállítása ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import index

class TestIndexLambdaHandler(unittest.TestCase):

    # ITT A LÉNYEG: Elmaszkoljuk a Gyár függvényét!
    @patch('index.get_active_channels')
    def test_lambda_handler_sends_messages_successfully(self, mock_get_channels):
        """
        Forgatókönyv: A Gyár sikeresen visszaad 2 csatornát, a küldés hibátlan.
        Elvárás: A Lambda jól formázza a szöveget, meghívja a send()-et, és 200 OK-t ad vissza.
        """
        # --- 1. ARRANGE (Előkészítés) ---
        # Létrehozunk két "buta" bábut (MagicMock). 
        # Nem érdekel minket, hogy ez Telegram vagy Discord, mert csak a Karmestert teszteljük!
        mock_channel_1 = MagicMock()
        mock_channel_2 = MagicMock()
        
        # Megmondjuk a Gyár bábujának, hogy ha meghívják, adja vissza ezt a két csatornát.
        mock_get_channels.return_value = [mock_channel_1, mock_channel_2]

        # A Lambda esemény, amit az AWS IoT dob nekünk
        event = {"status": "INACTIVE", "device_id": "test-device-01"}

        # --- 2. ACT (Cselekvés) ---
        # Futtatjuk a Lambda handlert! 
        # (A 'context' paraméter helyére beírhatunk None-t, mert a mi kódunk nem használja).
        response = index.lambda_handler(event, None)

        # --- 3. ASSERT (Ellenőrzés) ---
        # 1. Ellenőrizzük az AWS felé adott HTTP választ
        self.assertEqual(response['statusCode'], 200)
        self.assertIn("successfully sent to all 2 configured channels", response['body'])

        # 2. ÜZLETI LOGIKA ELLENŐRZÉSE: Jól formázta a szöveget?
        expected_message = "🚨 **ALERT** 🚨\nThe boiler is inactive!\nDevice: `test-device-01`"
        
        # 3. Ellenőrizzük, hogy A Karmester tényleg "vezényelt-e"!
        # Azt nézzük, hogy meghívta-e a send() metódust a helyes szöveggel.
        mock_channel_1.send.assert_called_once_with(expected_message)
        mock_channel_2.send.assert_called_once_with(expected_message)

    @patch('index.get_active_channels')
    def test_lambda_handler_formats_active_status_correctly(self, mock_get_channels):
        """
        Forgatókönyv: Nem 'INACTIVE' hiba jön, hanem egy normál (vagy ismeretlen) státusz.
        Elvárás: A Lambda a szirénás Markdown helyett a sima, egyszerű tájékoztató szöveget küldi el.
        """
        mock_channel = MagicMock()
        mock_get_channels.return_value = [mock_channel]

        # Most egy normál működést szimuláló eseményt küldünk
        event = {"status": "ACTIVE", "device_id": "boiler-01"}

        response = index.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        
        # ÜZLETI LOGIKA ELLENŐRZÉSE: Jól futott le az 'else' ág a formázásnál?
        expected_message = "Status info: ACTIVE (Device: boiler-01)"
        mock_channel.send.assert_called_once_with(expected_message)

    @patch('index.get_active_channels')
    def test_lambda_raises_value_error_if_no_channels_active(self, mock_get_channels):
        """
        Forgatókönyv: A Gyár egy üres listát ad vissza (nincs beállítva egyetlen csatorna sem).
        Elvárás: A Karmester (lambda_handler) azonnal ValueError-t dob, hogy jelezze a konfigurációs hibát.
        """
        # --- 1. ARRANGE ---
        # Azt mondjuk a bábunak, hogy most egy üres listát adjon vissza (szimulálva a hibás AWS-t)
        mock_get_channels.return_value = []
        
        event = {"status": "INACTIVE", "device_id": "test-device-01"}

        # --- 2. ACT & 3. ASSERT (Cselekvés és Ellenőrzés egyben) ---
        # Amikor kivételt (Exception-t) várunk, a Python unittest egy speciális 
        # "context manager"-t használ (a 'with' kulcsszót).
        
        with self.assertRaises(ValueError) as context:
            # Itt hívjuk meg a kódot. Ha ez NEM dob ValueError-t, a teszt elbukik!
            index.lambda_handler(event, None)

        # Ráadásként leellenőrizzük, hogy a hibaüzenet szövege is a megfelelő-e
        self.assertIn("No notification channels configured", str(context.exception))

    @patch('index.get_active_channels')
    def test_lambda_raises_exception_for_dlq_on_partial_failure(self, mock_get_channels):
        """
        Forgatókönyv: A Gyár visszaad 2 csatornát. Az egyik sikeresen küld, a másik viszont hálózati hibát dob a send() közben.
        Elvárás: A Karmester nem áll meg az első hibánál (mindkettőn megpróbálja a küldést), majd a végén kivételt dob az AWS DLQ számára.
        """
        # --- 1. ARRANGE ---
        # Két bábut hozunk létre: egy sikereset és egy hibásat
        mock_channel_success = MagicMock()
        mock_channel_fail = MagicMock()
        
        # A hibás bábunak azt mondjuk: "Amikor meghívják rajtad a send()-et, robbanj fel!"
        # Ezt a side_effect-tel érjük el a metóduson:
        mock_channel_fail.send.side_effect = Exception("Simulated network timeout")
        
        # A Gyár most ezt a vegyes párost adja vissza
        mock_get_channels.return_value = [mock_channel_success, mock_channel_fail]
        
        event = {"status": "INACTIVE", "device_id": "test-device-01"}
        
        # --- 2. ACT & 3. ASSERT ---
        # Elvárjuk, hogy a Lambda a futás legvégén dobjon egy Exception-t
        with self.assertRaises(Exception) as context:
            index.lambda_handler(event, None)
            
        # A LEGFONTOSABB ELLENŐRZÉS: 
        # Vajon a Karmester mindkét bábunak megpróbálta elküldeni az üzenetet?
        # Ha a kód megállt volna az első hibánál, akkor a success nem hívódott volna meg!
        mock_channel_success.send.assert_called_once()
        mock_channel_fail.send.assert_called_once()
        
        # Ellenőrizzük, hogy a hibaüzenetben pontosan az áll-e, amit az AWS-nek szántunk
        self.assertIn("Delivery failed for 1 channels", str(context.exception))
        self.assertIn("Simulated network timeout", str(context.exception))