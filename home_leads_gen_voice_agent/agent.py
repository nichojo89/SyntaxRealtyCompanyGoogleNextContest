from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.agents.run_config import RunConfig, StreamingMode

from home_leads_gen_voice_agent.prompts.supervisor_prompt import get_supervisor_prompt
from home_leads_gen_voice_agent.tools.agent_tools import open_url, initiate_phone_call
from home_leads_gen_voice_agent.tools.pipeline_tools import run_lead_generation, run_marketing_content

SUPERVISOR_MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"
BOT_NAME = "Evelyn"

supervisor = LlmAgent(
    name="Evelyn",
    model=SUPERVISOR_MODEL,
    instruction=get_supervisor_prompt(bot_name=BOT_NAME),
    tools=[
        run_lead_generation,
        run_marketing_content,
        open_url,
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