import os
import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock
from app.email_utils import send_verification_email

class TestEmailUtils(TestCase):

    @patch('app.email_utils.smtplib.SMTP_SSL')
    def test_send_verification_email(self, mock_smtp):
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        token = 'asc44ase2t23sdf43d'
        os.environ["EMAIL_USER"] = "illyatr25@gmail.com"
        os.environ["EMAIL_PASSWORD"] = "ekfj ofgi oxxz mohl"
        os.environ["SMTP_SERVER"] = "smtp.gmail.com"
        os.environ["SMTP_PORT"] = "465"

        # Вызовите функцию
        send_verification_email('test@example.com', token)

        # Отладка: выводите вызовы всех методов
        print("Mock calls:", mock_smtp_instance.mock_calls)

        # Проверьте, что методы вызваны правильно
        mock_smtp_instance.login.assert_called_once_with(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
        mock_smtp_instance.sendmail.assert_called_once()

if __name__ == '__main__':
    unittest.main()