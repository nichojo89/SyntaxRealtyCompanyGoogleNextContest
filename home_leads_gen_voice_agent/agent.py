import socket
import threading
import uvicorn
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.agents.run_config import RunConfig, StreamingMode

from home_leads_gen_voice_agent.api.server import app
from home_leads_gen_voice_agent.prompts.supervisor_prompt import get_supervisor_prompt
from home_leads_gen_voice_agent.tools.agent_tools import initiate_phone_call
from home_leads_gen_voice_agent.tools.pipeline_tools import run_lead_generation, run_marketing_content

SUPERVISOR_MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"
BOT_NAME = "Evelyn"


def _port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def _start_pipeline_server():
    """Starts FastAPI server because we send SubAgent calls via HTTP instead of AgentTool"""
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="warning")


if not _port_in_use(8001):
    thread = threading.Thread(target=_start_pipeline_server, daemon=True)
    thread.start()

#♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇
# Supervisor - Multi-Agent System ◇
#♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇

supervisor = LlmAgent(
    name="Evelyn",
    model=SUPERVISOR_MODEL,
    instruction=get_supervisor_prompt(bot_name=BOT_NAME, is_text_assistant=False),
    tools=[
        run_lead_generation,
        run_marketing_content,
        initiate_phone_call
    ],
)

run_config = RunConfig(
    speech_config=types.SpeechConfig(
        language_code="en-US",
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Charon"
            )
        ),
    ),
    response_modalities=["AUDIO", "TEXT"],
    streaming_mode=StreamingMode.BIDI,
    max_llm_calls=1_000,
)

root_agent = supervisor