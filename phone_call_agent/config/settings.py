"""
Application settings loaded from environment variables.
All required vars are validated at import time to fail fast.
"""

import os
import sys
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv(override=True)

_REQUIRED_VARS = [
    "DAILY_DOMAIN",
    "DAILY_API_KEY",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_CALLER_ID",
    "RECIPIENT_PHONE_NUMBER",
    "GOOGLE_API_KEY"
]


def _validate_env() -> None:
    """Validate required environment variables."""

    missing = [v for v in _REQUIRED_VARS if not os.getenv(v)]
    if missing:
        print(f"[config] Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


_validate_env()


@dataclass(frozen=True)
class DailySettings:
    """Settings required for Daily.Co room"""
    domain: str = os.getenv("DAILY_DOMAIN", "")
    api_key: str = os.getenv("DAILY_API_KEY", "")
    api_url: str = "https://api.daily.co/v1"
    room_ttl_seconds: int = 3600


@dataclass(frozen=True)
class TwilioSettings:
    """Settings required for Twilio SIP"""

    account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    caller_id: str = os.getenv("TWILIO_CALLER_ID", "")
    recipient_phone: str = os.getenv("RECIPIENT_PHONE_NUMBER", "")


@dataclass(frozen=True)
class GeminiSettings:
    """Settings required for Gemini LLM"""

    gemini_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    location: str = "us-east4"
    model: str = "gemini-2.5-flash-native-audio-preview-12-2025"
    voice_id: str = "Charon"
    temperature: float = 0.7
    max_tokens: int = 2048
    vad_silence_duration_ms: int = 500


# Initializes Settings
daily = DailySettings()
twilio = TwilioSettings()
gemini = GeminiSettings()
