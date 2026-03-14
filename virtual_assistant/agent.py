from google.genai import types
from google.genai.types import Modality
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.tools import AgentTool
from google.adk.tools import google_search
from virtual_assistant.models.PropertyForSale import PropertyForSale
from virtual_assistant.models.TextMessageEvaluation import TextMessageEvaluation
from virtual_assistant.prompts import (lead_generation_prompt, home_owner_details_prompt, create_text_message_prompt, evaluate_text_message_prompt, supervisor_prompt)
from virtual_assistant.tools.agent_tools import open_url, make_phone_call


def exit_loop() -> str:
    """Terminates the loop when text message evaluation score is 90 or above."""
    return "LOOP_TERMINATED_SUCCESSFULLY"

SUBAGENT_MODEL = "gemini-2.5-flash"
SUPERVISOR_MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"


# Get leads and contact information for leads (Sequential Agent)
lead_gen_subagent = LlmAgent(
    name="LeadGenerationSubAgent",
    model=SUBAGENT_MODEL,
    instruction=lead_generation_prompt.prompt,
    tools=[google_search],
    output_schema=PropertyForSale,
    output_key="lead_listings"
)

homeowner_details_subagent = LlmAgent(
    name="HomeownerDetailsSubAgent",
    model=SUBAGENT_MODEL,
    instruction=home_owner_details_prompt.prompt,
    tools=[google_search],
    output_key="enriched_leads"
)

lead_generation_sequential_agent = SequentialAgent(
    name="LeadGenerationSequentialAgent",
    sub_agents=[lead_gen_subagent, homeowner_details_subagent]
)

# Create text message to home-owner (Loop Agent)
content_creator_subagent = LlmAgent(
    name="ContentCreatorSubAgent",
    model=SUBAGENT_MODEL,
    instruction=create_text_message_prompt.prompt,
    output_key="pitch_draft"
)

content_reviewer_subagent = LlmAgent(
    name="ContentReviewerSubAgent",
    model=SUBAGENT_MODEL,
    instruction=evaluate_text_message_prompt.prompt,
    tools=[exit_loop],
    output_schema=TextMessageEvaluation
)

marketing_content_loop_agent = LoopAgent(
    name="MarketingContentLoopAgent",
    sub_agents=[content_creator_subagent, content_reviewer_subagent],
    max_iterations=4
)


supervisor = LlmAgent(
    name="Evelyn",
    model=SUPERVISOR_MODEL,
    instruction=supervisor_prompt.prompt,
    tools=[
        AgentTool(agent=lead_generation_sequential_agent),
        AgentTool(agent=marketing_content_loop_agent),
        open_url,
        make_phone_call
    ],
)

# Add speech and modality runtime behavior
run_config = RunConfig(
    speech_config=types.SpeechConfig(
        language_code="en-US",
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Charon"
            )
        ),
    ),
    response_modalities=[Modality.AUDIO],
    streaming_mode=StreamingMode.BIDI,
    max_llm_calls=1000,
)

root_agent = supervisor