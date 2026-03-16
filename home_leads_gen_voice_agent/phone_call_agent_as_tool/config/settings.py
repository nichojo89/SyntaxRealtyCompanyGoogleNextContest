import sys
from dataclasses import dataclass
from dotenv import load_dotenv
from home_leads_gen_voice_agent.phone_call_agent_as_tool.config.secret_manager import get_secret

load_dotenv(override=True)

_REQUIRED_VARS = [
    "GOOGLE_GENAI_USE_VERTEXAI",
    "GOOGLE_API_KEY",
    "DAILY_DOMAIN",
    "DAILY_API_KEY",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_CALLER_ID",
]


def _validate_env() -> None:
    missing = []
    for v in _REQUIRED_VARS:
        try:
            get_secret(v)
        except Exception:
            missing.append(v)
    if missing:
        print(f"[config] Missing required secrets: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


_validate_env()


@dataclass(frozen=True)
class DailySettings:
    domain: str = get_secret("DAILY_DOMAIN")
    api_key: str = get_secret("DAILY_API_KEY")
    api_url: str = "https://api.daily.co/v1"
    room_ttl_seconds: int = 3600


@dataclass(frozen=True)
class TwilioSettings:
    account_sid: str = get_secret("TWILIO_ACCOUNT_SID")
    auth_token: str = get_secret("TWILIO_AUTH_TOKEN")
    caller_id: str = get_secret("TWILIO_CALLER_ID")


@dataclass(frozen=True)
class GeminiSettings:
    gemini_api_key: str = get_secret("GOOGLE_API_KEY")
    use_vertex_ai: str = get_secret("GOOGLE_GENAI_USE_VERTEXAI")
    location: str = "us-central1"
    model: str = "gemini-2.5-flash-native-audio-preview-09-2025"
    voice_id: str = "Charon"
    temperature: float = 0.7
    max_tokens: int = 2048
    vad_silence_duration_ms: int = 500


daily = DailySettings()
twilio = TwilioSettings()
gemini = GeminiSettings()