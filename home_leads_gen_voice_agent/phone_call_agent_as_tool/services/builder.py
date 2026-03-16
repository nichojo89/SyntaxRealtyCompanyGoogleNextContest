import asyncio
import subprocess
import sys
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.logger import FrameLogger
from pipecat.services.gemini_multimodal_live.gemini import GeminiVADParams
from pipecat.services.google.gemini_live.llm import InputParams, GeminiLiveLLMService
from pipecat.transports.daily.transport import DailyParams, DailyTransport
from pipecat.frames.frames import LLMMessagesUpdateFrame, TextFrame

from home_leads_gen_voice_agent.phone_call_agent_as_tool.config.settings import daily as daily_cfg
from home_leads_gen_voice_agent.phone_call_agent_as_tool.config.settings import gemini as gemini_cfg
from home_leads_gen_voice_agent.phone_call_agent_as_tool.models.fsbo_prompt_parameters import FSBOPromptParameters
from home_leads_gen_voice_agent.phone_call_agent_as_tool.pipeline.daily_service import RoomInfo
from home_leads_gen_voice_agent.phone_call_agent_as_tool.pipeline.twilio_service import TwilioService
from home_leads_gen_voice_agent.prompts import negotiate_deal_prompt



def _get_voice_call_system_instruction(fsbo_prompt_parameters: FSBOPromptParameters) -> str:
    """    Gets system instruction from the to negotiate deals for homes that have been listed online for a long time.
    Returns: system_instruction    """
    bot_name = "Benjamin"
    realtor_name = "Emily West"
    realty_company = "Syntax Realty Company"
    prompt = negotiate_deal_prompt.get_negotiation_prompt(
        bot_name=bot_name,
        realtor_name=realtor_name,
        realty_company=realty_company,
        property_address=fsbo_prompt_parameters.sale_property_address,
        available_appointment_times=fsbo_prompt_parameters.available_appointment_times,
        property_sale_listing_price=fsbo_prompt_parameters.property_sale_listing_price,
        property_sale_listing_date=fsbo_prompt_parameters.property_sale_listing_date,
        sale_property_condition=fsbo_prompt_parameters.sale_property_condition,
        sale_property_acquired_by_owner_amount=fsbo_prompt_parameters.sale_property_condition,
        sale_property_acquired_by_owner_year=fsbo_prompt_parameters.sale_property_acquired_by_owner_year,
        local_rent_estimation=fsbo_prompt_parameters.local_rent_estimation
    )

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


def build_llm(fsbo_prompt_parameters: FSBOPromptParameters) -> GeminiLiveLLMService:
    """Builds the Gemini Live LLM service."""
    prompt = _get_voice_call_system_instruction(fsbo_prompt_parameters=fsbo_prompt_parameters)

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
        fsbo_prompt_parameters: FSBOPromptParameters
) -> tuple[PipelineTask, DailyTransport]:
    transport = build_transport(room, owner_token)
    llm = build_llm(fsbo_prompt_parameters=fsbo_prompt_parameters)

    pipeline = Pipeline([
        FrameLogger("LOG FRAME 0"),
        transport.input(),
        FrameLogger("LOG FRAME 1"),
        llm,
        FrameLogger("LOG FRAME 2"),
        transport.output(),
        FrameLogger("LOG FRAME 3")
    ])
    task = PipelineTask(pipeline)

    # Track if bot is speaking to prevent premature cancellation
    bot_is_speaking = False

    @transport.event_handler("on_joined")
    async def on_joined(_, __):
        print("[Pipeline] Bot joined room — initiating Twilio bridge call...")
        print(f"[DEBUG] SIP URI: {room.sip_uri}")
        print(f"[DEBUG] Recipient: {recipient_phone}")

        try:
            result = await asyncio.to_thread(twilio.bridge_call, room.sip_uri, recipient_phone)
            print(f"[DEBUG] Twilio bridge result: {result}")
        except Exception as e:
            print(f"[ERROR] Twilio bridge failed: {e}")

    @transport.event_handler("on_first_participant_joined")
    async def on_first_participant_joined(_, participant):
        name = participant.get("info", {}).get("userName", "unknown")
        print(f"[Pipeline] First participant joined: {name}")

        async def trigger_bot_greeting():
            print("[Pipeline] Waiting for Cloud Run WebRTC TCP fallback...")
            # Wait 4 seconds to guarantee the Cloud Run audio network is fully open
            await asyncio.sleep(4.0)

            print("[Pipeline] Prompting bot to speak first...")
            # Use TextFrame instead! Gemini will consume this and speak out loud.
            await task.queue_frames([TextFrame(text="Hi, I just answered the phone. Please introduce yourself.")])

        # Fire and forget
        asyncio.create_task(trigger_bot_greeting())

    @task.event_handler("on_bot_started_speaking")
    async def on_bot_started_speaking(task):
        nonlocal bot_is_speaking
        bot_is_speaking = True
        print("[Pipeline] Bot started speaking - preventing premature cancellation")

    @task.event_handler("on_bot_stopped_speaking")
    async def on_bot_stopped_speaking(task):
        nonlocal bot_is_speaking
        bot_is_speaking = False
        print("[Pipeline] Bot stopped speaking")

    @transport.event_handler("on_participant_left")
    async def on_participant_left(_, __, reason):
        print(f"[Pipeline] Participant left ({reason})")

        # If bot is speaking, wait for it to finish
        if bot_is_speaking:
            print("[Pipeline] Bot is speaking, waiting before cancelling...")
            # Wait up to 10 seconds for bot to finish
            for i in range(100):  # 10 seconds with 0.1s intervals
                if not bot_is_speaking:
                    print("[Pipeline] Bot finished speaking, cancelling pipeline")
                    break
                await asyncio.sleep(0.1)
            else:
                print("[Pipeline] Timeout waiting for bot to finish, cancelling anyway")
        else:
            # Give bot a chance to respond even if not speaking yet
            print("[Pipeline] Bot not speaking, giving 5 seconds to respond...")
            await asyncio.sleep(5)

        print("[Pipeline] Cancelling pipeline.")
        await task.cancel()

        # Add frame debugging to trace audio flow

    @task.event_handler("on_frame_reached_upstream")
    async def on_frame_upstream(task, frame):
        frame_type = type(frame).__name__
        if frame_type in ['InputAudioRawFrame', 'UserAudioRawFrame']:
            print(f"[DEBUG] Audio input frame: {frame_type}")

    @task.event_handler("on_frame_reached_downstream")
    async def on_frame_downstream(task, frame):
        frame_type = type(frame).__name__
        if hasattr(frame, 'audio'):
            print(f"[Pipeline] Audio frame detected: {frame_type}")
        elif frame_type in ['BotStartedSpeakingFrame', 'BotStoppedSpeakingFrame', 'TTSAudioRawFrame']:
            print(f"[Pipeline] Speaking/TTS frame: {frame_type}")

    return task, transport