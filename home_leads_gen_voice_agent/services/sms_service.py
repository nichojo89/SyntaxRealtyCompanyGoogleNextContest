import os
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

class TwilioSmsService:
    """A service class to handle sending SMS via Twilio."""

    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.caller_id = os.getenv("TWILIO_CALLER_ID")

        if not all([self.account_sid, self.auth_token, self.caller_id]):
            print("Missing Twilio credentials. Check your environment variables.")
            raise ValueError("Incomplete Twilio configuration.")

        self.client = Client(self.account_sid, self.auth_token)

    def send_message(self, to_number: str, message_body: str) -> Optional[str]:
        """
        Sends an SMS message to a specified number.

        :param to_number: The recipient's phone number (E.164 format, e.g., +1234567890).
        :param message_body: The text content of the message.
        :return: The message SID if successful.
        :raises: Rethrows exceptions after logging.
        """
        if not to_number or not message_body:
            raise ValueError("Both 'to_number' and 'message_body' are required.")

        try:
            message = self.client.messages.create(
                body=message_body,
                from_=self.caller_id,
                to=to_number
            )
            print(f"SMS successfully sent to {to_number}. SID: {message.sid}")
            return message.sid

        except TwilioRestException as e:
            print(f"Twilio API error while sending SMS to {to_number}: {e.msg} (Code: {e.code})")
            raise
        except Exception as e:
            print(f"Unexpected error while sending SMS to {to_number}: {str(e)}")
            raise