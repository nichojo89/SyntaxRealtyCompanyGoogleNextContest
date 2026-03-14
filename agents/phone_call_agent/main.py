"""
main.py — entrypoint.

Initiates an AI Voice call 📲
"""

import asyncio
import time
from pipecat.pipeline.runner import PipelineRunner
from agents.phone_call_agent.pipeline.daily_service import DailyService
from agents.phone_call_agent.pipeline.twilio_service import TwilioService
from agents.phone_call_agent.services.builder import build_pipeline


async def call(phone_number: str) -> None:
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
    )

    print("Starting pipeline runner...")
    result = await PipelineRunner().run(task)
    print(f"Ending pipeline runner... {result}")


if __name__ == "__main__":
    asyncio.run(call(phone_number="+12488906977"))
