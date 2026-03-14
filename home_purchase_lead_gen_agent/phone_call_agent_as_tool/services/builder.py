"""
Pipecat pipeline factory.

Builds the audio pipeline (Daily transport ❧ Gemini LLM ❧ Daily transport)
and wires the lifecycle event handlers that drive the Twilio bridge call.
"""

import asyncio
import subprocess
import sys
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask
from pipecat.services.gemini_multimodal_live.gemini import GeminiVADParams
from pipecat.services.google.gemini_live.llm import InputParams, GeminiLiveLLMService
from pipecat.transports.daily.transport import DailyParams, DailyTransport
from home_purchase_lead_gen_agent.phone_call_agent_as_tool.config.settings import daily as daily_cfg
from home_purchase_lead_gen_agent.phone_call_agent_as_tool.config.settings import gemini as gemini_cfg
from home_purchase_lead_gen_agent.phone_call_agent_as_tool.pipeline.daily_service import RoomInfo
from home_purchase_lead_gen_agent.phone_call_agent_as_tool.pipeline.twilio_service import TwilioService
from home_purchase_lead_gen_agent.prompts import negotiate_deal_prompt


# ==========================================
# 0. Ensure Playwright Browsers are Installed
# ==========================================
def ensure_playwright_browsers():
    print("Checking for Playwright browser binaries...")
    try:
        # Runs `python -m playwright install chromium` in the background
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            stdout=subprocess.DEVNULL,  # Hides the output if already installed
            stderr=subprocess.PIPE
        )
        print("Playwright browsers are ready!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing Playwright: {e.stderr.decode()}")


# Run the check before defining the agents
ensure_playwright_browsers()


def _get_system_instruction() -> str:
    """
    Gets system instruction from the to negotiate deals for homes that have been listed online for a long time.

    Returns: system_instruction
    """
    bot_name = "Jebadiah"
    realtor_name = "Emily West"
    realty_company = "Syntax Realty Company"
    prompt = (negotiate_deal_prompt.prompt
              .replace("ASSISTANT_NAME", bot_name)
              .replace("REALTOR_NAME", realtor_name)
              .replace("REALTOR_COMPANY", realty_company))

    return prompt


def build_transport(room: RoomInfo, owner_token: str) -> DailyTransport:
    """Builds the daily transport for the given room."""

    return DailyTransport(
        room_url=room.url,
        token=owner_token,
        bot_name="AIAssistant",
        params=DailyParams(
            api_key=daily_cfg.api_key,
            api_url=daily_cfg.api_url,
            audio_in_enabled=True,
            audio_out_enabled=True,
            camera_out_enabled=False,
            transcription_enabled=False,
        ),
    )


def build_llm() -> GeminiLiveLLMService:
    """Builds the Gemini Live LLM service."""

    prompt = _get_system_instruction()

    return GeminiLiveLLMService(
        api_key=gemini_cfg.gemini_api_key,  # Use api_key instead of credentials
        model=gemini_cfg.model,
        voice_id=gemini_cfg.voice_id,
        system_instruction=prompt,
        params=InputParams(
            temperature=gemini_cfg.temperature,
            max_tokens=gemini_cfg.max_tokens,
            vad=GeminiVADParams(silence_duration_ms=gemini_cfg.vad_silence_duration_ms),
        ),
    )


def build_pipeline(
        room: RoomInfo,
        owner_token: str,
        twilio: TwilioService,
        recipient_phone: str,
) -> tuple[PipelineTask, DailyTransport]:
    """
    Assemble the full Pipecat pipeline and register event handlers.

    returns runnable PipelineTask and the transport (so the caller can hand it to PipelineRunner if needed).
    """

    transport = build_transport(room, owner_token)
    llm = build_llm()

    pipeline = Pipeline([transport.input(), llm, transport.output()])
    task = PipelineTask(pipeline)

    @transport.event_handler("on_joined")
    async def on_joined(_, __):
        print("[Pipeline] Bot joined room — initiating Twilio bridge call...")
        await asyncio.to_thread(twilio.bridge_call, room.sip_uri, recipient_phone)

    @transport.event_handler("on_first_participant_joined")
    async def on_first_participant_joined(_, participant):
        name = participant.get("info", {}).get("userName", "unknown")
        print(f"[Pipeline] First participant joined: {name}")

    @transport.event_handler("on_participant_left")
    async def on_participant_left(_, __, reason):
        print(f"[Pipeline] Participant left ({reason}) — cancelling pipeline.")
        await task.cancel()

    return task, transport
