from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from google.genai.types import Modality
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.tools import AgentTool
from google.adk.tools import google_search
from home_purchase_lead_gen_agent.models.PropertyForSale import PropertyForSale
from home_purchase_lead_gen_agent.models.TextMessageEvaluation import TextMessageEvaluation
from home_purchase_lead_gen_agent.prompts import (lead_generation_prompt, home_owner_details_prompt, create_text_message_prompt, evaluate_text_message_prompt)
from home_purchase_lead_gen_agent.prompts.supervisor_prompt import get_supervisor_prompt
from home_purchase_lead_gen_agent.tools.agent_tools import open_url, initiate_phone_call

SUBAGENT_MODEL = "gemini-2.5-flash"
SUPERVISOR_MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"
BOT_NAME = "Evelyn"

def _build_multi_agent() -> LlmAgent | None:
    """
    Builds Multi-AgentSystem designed to find homes for sale that have been on the market for a long period of time.

    Users can perform the following tasks:
    ❥ View home listings found by the LLMs in a browser.
    ❥ Call the owner of the home with an AI voice assistant
    ❥ Send a carefully crafted text message to the owner of the home.

    returns: root agent.
    """
    try:
        #♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡
        # Sequential Agent ❥ Get leads and contact information for leads ♡
        #♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡

        def log_lead_listings(context: CallbackContext, *args, **kwargs):
            """Callback to peek at the state after the agent finishes."""
            print("\n" + "=" * 50)
            print("🕵️ DEBUG: lead_gen_subagent Output (PropertyForSale):")
            # Retrieve the exact structured data saved to the output_key
            print(context.state.get("lead_listings"))
            print(args)
            print(kwargs)
            print("=" * 50 + "\n")

        lead_gen_subagent = LlmAgent(
            name="LeadGenerationSubAgent",
            model=SUBAGENT_MODEL,
            instruction=lead_generation_prompt.prompt,
            tools=[google_search],
            output_schema=PropertyForSale,
            output_key="lead_listings",
            before_agent_callback=log_lead_listings,
            after_agent_callback=log_lead_listings
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

        #♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡
        # Loop Agent ❥ Create text message to home-owner ♡
        #♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡

        def exit_loop() -> str:
            """Terminates the loop when text message evaluation score is 90 or above."""
            return "LOOP_TERMINATED_SUCCESSFULLY"

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

        #♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇
        # Supervisor - Multi-Agent System ◇
        #♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇

        supervisor = LlmAgent(
            name="Evelyn",
            # model=SUPERVISOR_MODEL,
            model=SUPERVISOR_MODEL,
            instruction=get_supervisor_prompt(bot_name=BOT_NAME),
            tools=[
                AgentTool(agent=lead_generation_sequential_agent),
                AgentTool(agent=marketing_content_loop_agent),
                open_url,
                initiate_phone_call
            ],
        )
        return supervisor
    except Exception as e:
        print(f'‼️Error building home leads multi-agent system {e}')

# Adds runtime behaviors for speech
run_config = RunConfig(
    speech_config=types.SpeechConfig(
        language_code="en-US",
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Charon"
            )
        ),
    ),
    response_modalities=[Modality.AUDIO, Modality.TEXT],
    streaming_mode=StreamingMode.BIDI,
    max_llm_calls=1_000,
)
supervisor_evelyn = _build_multi_agent()
if supervisor_evelyn:
    root_agent = supervisor_evelyn