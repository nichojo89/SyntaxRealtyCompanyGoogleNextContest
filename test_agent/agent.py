from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.tools import AgentTool
from google.adk.tools import google_search

from home_purchase_lead_gen_agent.models.LeadTextRequest import LeadTextRequest
from home_purchase_lead_gen_agent.models.TextMessageEvaluation import TextMessageEvaluation
from home_purchase_lead_gen_agent.prompts import (lead_generation_prompt, create_text_message_prompt, evaluate_text_message_prompt, lead_details_prompt)
from home_purchase_lead_gen_agent.prompts.supervisor_prompt import get_supervisor_prompt
from home_purchase_lead_gen_agent.tools.agent_tools import open_url, initiate_phone_call, send_text_message

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

        def log_lead_listings(*args, **kwargs):
            """Callback to inspect the context and print the extracted data."""
            print("\n" + "▼" * 50)
            print("🕵️ DEBUG: Extractor Agent Callback Triggered!")

            # ADK passes the context object in the keyword arguments
            context = kwargs.get('callback_context')
            if not context:
                print("❌ ERROR: No 'callback_context' found in kwargs!")
                print("▲" * 50 + "\n")
                return

            # The context object has a 'state' attribute which holds all session data.
            # We can retrieve our data using the `output_key` we defined.
            print("✅ Found context object. Inspecting its state...")
            lead_data = context.state.get("for_sale_by_owner_lead_listings")

            if lead_data:
                print("\n🎉 SUCCESS! Found 'lead_listings' data:")
                # lead_data will be an instance (or list of instances) of your PropertyForSale model.
                # Printing it directly will give a nice, structured representation.
                print(lead_data)
            else:
                print("\n⚠️ WARNING: 'lead_listings' key not found in agent state.")
                # This helps debug if you have a typo in your output_key
                print("   Available state keys:", list(context.state.keys()))

            print("▲" * 50 + "\n")

        def log_lead_details(*args, **kwargs):
            """Callback to inspect the context and print the extracted data."""
            print("\n" + "▼" * 50)
            print("🕵️ DEBUG: Extractor Agent Callback Triggered!")

            # ADK passes the context object in the keyword arguments
            context = kwargs.get('callback_context')
            if not context:
                print("❌ ERROR: No 'callback_context' found in kwargs!")
                print("▲" * 50 + "\n")
                return

            # The context object has a 'state' attribute which holds all session data.
            # We can retrieve our data using the `output_key` we defined.
            print("✅ Found context object. Inspecting its state...")
            lead_data = context.state.get("lead_listings")

            if lead_data:
                print("\n🎉 SUCCESS! Found 'lead_listings' data:")
                # lead_data will be an instance (or list of instances) of your PropertyForSale model.
                # Printing it directly will give a nice, structured representation.
                print(lead_data)
            else:
                print("\n⚠️ WARNING: 'lead_listings' key not found in agent state.")
                # This helps debug if you have a typo in your output_key
                print("   Available state keys:", list(context.state.keys()))

            print("▲" * 50 + "\n")

        lead_search_subagent = LlmAgent(
            name="LeadSearchSubAgent",
            model=SUBAGENT_MODEL,
            instruction=lead_generation_prompt.prompt,
            tools=[google_search],
            # output_schema=PropertyLeads,
            output_key="for_sale_by_owner_lead_listings"
        )
        log_agent = LlmAgent(
            name="LogAgent",
            model=SUBAGENT_MODEL,
            instruction="Your ONLY mission is to pass the {{for_sale_by_owner_lead_listings}} data through **EXACTLY** as it is. Do not modify it",
            # output_schema=PropertyLeads,
            output_key="for_sale_by_owner_lead_listings",
            after_agent_callback=log_lead_listings
        )

        # 2. Extraction Agent (Uses structured output, NO built-in search tool)
        lead_extraction_subagent = LlmAgent(
            name="LeadExtractionSubAgent",
            model=SUBAGENT_MODEL,
            instruction=lead_details_prompt.prompt,
            tools=[google_search],
            # output_schema=PropertyDetailsList,
            output_key="lead_listings",
            after_agent_callback=log_lead_details
        )

        lead_generation_sequential_agent = SequentialAgent(
            name="LeadGenerationSequentialAgent",
            sub_agents=[lead_search_subagent, log_agent, lead_extraction_subagent],
        )

        # ♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡
        # Loop Agent ❥ Create text message to home-owner ♡
        # ♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡◇♤♧♡

        def exit_loop() -> str:
            """Terminates the loop when text message evaluation score is 90 or above."""
            return "LOOP_TERMINATED_SUCCESSFULLY"

        content_creator_subagent = LlmAgent(
            name="ContentCreatorSubAgent",
            model=SUBAGENT_MODEL,
            instruction=create_text_message_prompt.prompt,
            output_key="pitch_draft",
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
            instruction=get_supervisor_prompt(bot_name=BOT_NAME),
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

# Adds runtime behaviors for speech
# run_config = RunConfig(
#     speech_config=types.SpeechConfig(
#         language_code="en-US",
#         voice_config=types.VoiceConfig(
#             prebuilt_voice_config=types.PrebuiltVoiceConfig(
#                 voice_name="Charon"
#             )
#         ),
#     ),
#     response_modalities=[Modality.AUDIO, Modality.TEXT],
#     streaming_mode=StreamingMode.BIDI,
#     max_llm_calls=1_000,
# )
supervisor_evelyn = _build_multi_agent()
if supervisor_evelyn:
    root_agent = supervisor_evelyn