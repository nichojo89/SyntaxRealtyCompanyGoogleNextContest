import time
from twilio.rest import Client
from home_leads_gen_voice_agent.phone_call_agent_as_tool.config.settings import twilio as cfg


class TwilioService:
    """Connects a human over telephone and an LLM inside a WebRTC room via Daily SIP endpoint through a Twilio Conference"""

    def __init__(self) -> None:
        self._client = Client(cfg.account_sid, cfg.auth_token)

    def bridge_call(self, daily_sip_uri: str, recipient_phone: str) -> str:
        """
        Join LLM and telephone user into WebRTC Daily room.
        SIP URI — and drop both into the same silent Twilio Conference.

        returns the recipient call SID.
        """

        conference_name = f"BotConf_{int(time.time())}"
        twiml = self._build_conference_twiml(conference_name)

        recipient_call = self._client.calls.create(
            to=recipient_phone,
            from_=cfg.caller_id,
            twiml=twiml,
        )
        print(f"Twilio ❥ Recipient call — sid={recipient_call.sid}  status={recipient_call.status}")

        bot_call = self._client.calls.create(
            to=daily_sip_uri,
            from_=cfg.caller_id,
            twiml=twiml,
        )
        print(f"Twilio ❥ Bot call — sid={bot_call.sid}  status={bot_call.status}")

        return recipient_call.sid

    @staticmethod
    def _build_conference_twiml(conference_name: str) -> str:
        """
        Build TwiML that drops a caller into a silent conference room.
        ❥ waitUrl: absolute silence instead of hold music
        ❥ beep: no entry chime when bot connects
        ❥ endConferenceOnExit: conference ends when either party hangs up
        """

        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<Response><Dial>"
            '<Conference startConferenceOnEnter="true" endConferenceOnExit="true" '
            f'waitUrl="" beep="false" record="record-from-start">{conference_name}</Conference>'
            "</Dial></Response>"
        )