from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.tools import AgentTool
from google.adk.tools import google_search
from home_leads_gen_voice_agent.models.LeadTextRequest import LeadTextRequest
from home_leads_gen_voice_agent.prompts import (lead_generation_prompt, create_text_message_prompt, evaluate_text_message_prompt, lead_details_prompt)
from home_leads_gen_voice_agent.prompts.supervisor_prompt import get_supervisor_prompt
from home_leads_gen_voice_agent.tools.agent_tools import open_url, initiate_phone_call, send_text_message

SUBAGENT_MODEL = "gemini-2.5-flash"
SUBAGENT_LITE_MODEL = "gemini-2.5-flash-lite"
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

        lead_search_subagent = LlmAgent(
            name="LeadSearchSubAgent",
            model=SUBAGENT_MODEL,
            instruction=lead_generation_prompt.prompt,
            tools=[google_search],
            output_key="for_sale_by_owner_lead_listings"
        )
        lead_extraction_subagent = LlmAgent(
            name="LeadExtractionSubAgent",
            model=SUBAGENT_MODEL,
            instruction=lead_details_prompt.prompt,
            tools=[google_search],
            output_key="lead_listings",
        )

        lead_generation_sequential_agent = SequentialAgent(
            name="LeadGenerationSequentialAgent",
            sub_agents=[lead_search_subagent, lead_extraction_subagent],
        )

        # ♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡
        # Loop Agent ❥ Create text message to home-owner ♡
        # ♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡

        def exit_loop(final_text_message: str) -> str:
            """Terminates the loop when text message evaluation score is 90 or above. You MUST pass the final text message into this tool."""

            return f"FINAL_APPROVED_TEXT: {final_text_message}"

        content_creator_subagent = LlmAgent(
            name="ContentCreatorSubAgent",
            model=SUBAGENT_MODEL,
            instruction=create_text_message_prompt.prompt,
            output_key="text_draft",
            input_schema=LeadTextRequest
        )

        content_reviewer_subagent = LlmAgent(
            name="ContentReviewerSubAgent",
            model=SUBAGENT_LITE_MODEL,
            instruction=evaluate_text_message_prompt.prompt,
            tools=[exit_loop],
            # output_schema=TextMessageEvaluation

            output_key="text_message_to_send"
        )


        marketing_content_loop_agent = LoopAgent(
            name="MarketingContentLoopAgent",
            description="Drafts and refines a marketing text message. You must pass the selected lead's property_address, owner_name, and time_on_market to this tool.",
            sub_agents=[content_creator_subagent, content_reviewer_subagent],
            max_iterations=4
        )

        #♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇
        # Supervisor - Multi-Agent System ◇
        #♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇

        supervisor = LlmAgent(
            name="Evelyn",
            # model=SUPERVISOR_MODEL,
            model=SUBAGENT_MODEL,
            description="Assist Realtor user by finding For-Sale-By-Owner leads, calling and text leads, showing home listings in a web browser",
            instruction=get_supervisor_prompt(bot_name=BOT_NAME, is_text_assistant=True),
            tools=[
                AgentTool(agent=lead_generation_sequential_agent),
                AgentTool(agent=marketing_content_loop_agent),
                open_url,
                initiate_phone_call,
                send_text_message
            ],
        )
        return supervisor
    except Exception as e:
        print(f'‼️Error building home leads multi-agent system {e}')

supervisor_evelyn = _build_multi_agent()
if supervisor_evelyn:
    root_agent = supervisor_evelyn