import time
from pipecat.pipeline.runner import PipelineRunner
from home_leads_gen_voice_agent.phone_call_agent_as_tool.pipeline.daily_service import DailyService
from home_leads_gen_voice_agent.phone_call_agent_as_tool.pipeline.twilio_service import TwilioService
from home_leads_gen_voice_agent.phone_call_agent_as_tool.services.builder import build_pipeline

async def call(phone_number: str, fsbo_prompt_parameters) -> None:
    """Runs the outbound voice bot"""

    room_name = f"VoiceBot-{int(time.time())}"

    daily_svc = DailyService()
    twilio_svc = TwilioService()

    room = await daily_svc.create_sip_room(room_name)
    owner_token = await daily_svc.create_owner_token(room_name)

    task, _ = build_pipeline(
        room=room,
        owner_token=owner_token,
        twilio=twilio_svc,
        recipient_phone=phone_number,
        fsbo_prompt_parameters=fsbo_prompt_parameters,
    )

    print("Starting call...")
    result = await PipelineRunner().run(task)
    print(f"Ending call... {result}")