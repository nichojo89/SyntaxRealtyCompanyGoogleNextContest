import os
from datetime import date, datetime
from typing import Annotated, re

from google.genai import types
from google.genai.types import Modality
from pydantic import BaseModel, Field, AfterValidator
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.tools import AgentTool
from google.adk.tools import google_search

from phone_call_agent.main import call


# ==============================================================================
# Pydantic Models & Validators
# ==============================================================================

def parse_mm_dd_yyyy(value: str) -> date:
    try:
        dt_object = datetime.strptime(value, "%m/%d/%Y")
        return dt_object.date()
    except ValueError:
        raise ValueError(f"Date string does not match format 'mm/dd/yyyy': {value}")


Date_mm_dd_yyyy = Annotated[date, AfterValidator(parse_mm_dd_yyyy)]


class PropertyForSale(BaseModel):
    sale_property_address: str = Field(
        description="Address of the property",
        alias="SALE_PROPERTY_ADDRESS",
        default="52 E Burdick St, Oxford, MI 48371"
    )
    sale_property_sale_listing_price: str = Field(
        description="Sale price of the property",
        alias="SALE_PROPERTY_SALE_LISTING_PRICE",
        default="$235,000"
    )
    sale_property_sale_listing_date: Date_mm_dd_yyyy = Field(
        description="Date the property was listed",
        alias="SALE_PROPERTY_SALE_LISTING_DATE",
        default=datetime.now().date()
    )
    sale_property_condition: str = Field(
        description="Condition of the property",
        alias="SALE_PROPERTY_CONDITION",
        default="Fair condition"
    )
    sale_property_acquired_by_owner_amount: str = Field(
        description="Amount the owner acquired the property for",
        alias="SALE_PROPERTY_ACQUIRED_BY_OWNER_AMOUNT",
        default="$138,000"
    )
    sale_property_acquired_by_owner_year: int = Field(
        description="Year the owner acquired the property",
        alias="SALE_PROPERTY_ACQUIRED_BY_OWNER_YEAR",
        default=2022
    )
    local_rent_estimation: str = Field(
        description="Local rent estimation",
        alias="LOCAL_RENT_ESTIMATION",
        default="$1,300"
    )
    comparable_property_address: str = Field(
        description="Comparable property address",
        alias="COMPARABLE_PROPERTY_ADDRESS",
        default="1234 Lapeer rd. Oxford MI"
    )
    buyers_name: str = Field(
        description="Buyer's name or realtor name",
        alias="BUYERS_NAME",
        default="REALTOR_NAME"
    )
    buyers_loan_application_amount: str = Field(
        description="Buyer's loan application amount",
        alias="BUYERS_LOAN_APPLICATION_AMOUNT",
        default="$145,000"
    )
    buyers_loan_amount: str = Field(
        description="Buyer's loan amount",
        alias="BUYERS_LOAN_AMOUNT",
        default="$150,000"
    )
    buyers_down_payment: str = Field(
        description="Buyer's down payment",
        alias="BUYERS_DOWN_PAYMENT",
        default="$30,000"
    )
    low_ball_amount: str = Field(
        description="Low ball offer amount",
        alias="LOW_BALL_AMOUNT",
        default="$130,000"
    )


class PitchEvaluation(BaseModel):
    score: int = Field(description="Effectiveness score from 1 to 100")
    reason: str = Field(description="Reason for the score, and feedback if under 90")
    approved: bool = Field(description="True if score is 90 or above")


# ==============================================================================
# Tool Functions
# ==============================================================================

def exit_loop() -> str:
    """Terminates the loop when pitch score is 90 or above."""
    return "LOOP_TERMINATED_SUCCESSFULLY"


# ==============================================================================
# Lead Generation Sequential Agent
# ==============================================================================

lead_gen_subagent = LlmAgent(
    name="LeadGenerationSubAgent",
    model="gemini-2.5-flash",
    instruction="""You are a Lead Generation AI.
You must use the google_search tool to look for real 'For Sale By Owner' (FSBO) home listings based on the location the user provides.
Try searching for terms like "For sale by owner [location] real estate" or "FSBO listings [location]".

CRITICAL INSTRUCTIONS:
1. Read the search snippets carefully.
2. Extract the home address, seller contact information (if available), days on market, and URL.
3. If contact info or days on market are missing from the snippet, just write "Not listed". Do NOT make up data.
4. Format the output as a clear, numbered list.
""",
    tools=[google_search],
    output_schema=PropertyForSale,
    output_key="lead_listings"
)

homeowner_details_subagent = LlmAgent(
    name="HomeownerDetailsSubAgent",
    model="gemini-2.5-flash",
    instruction="""You are an Investigative Real Estate AI.
You have received a list of properties from the previous agent.

CRITICAL INSTRUCTIONS:
1. For each property, use the google_search tool to search the specific address and try to find the current homeowner's name.
2. If you cannot find the exact homeowner's name due to privacy, extract as much detail about the property itself as possible (e.g., bed/bath count, square footage, neighborhood details).
3. Combine the original listing data with the new details you found.
4. Return a final, comprehensive summary of the enriched leads.
""",
    tools=[google_search],
    output_key="enriched_leads"
)

lead_generation_sequential_agent = SequentialAgent(
    name="LeadGenerationSequentialAgent",
    sub_agents=[lead_gen_subagent, homeowner_details_subagent]
)

# ==============================================================================
# Marketing Content Loop Agent
# ==============================================================================

content_creator_subagent = LlmAgent(
    name="ContentCreatorSubAgent",
    model="gemini-2.5-flash",
    instruction="""You are an expert Real Estate Copywriter.
Write a highly persuasive, 3-sentence outreach elevator pitch for the provided listing.
The goal is to convince the homeowner to hire our realtor to sell their house.
Use any specific details you have about the property or homeowner to personalize it.

CRITICAL: If the Content Reviewer has provided feedback in the conversation history, you MUST apply that feedback to improve the pitch!
""",
    output_key="pitch_draft"
)

content_reviewer_subagent = LlmAgent(
    name="ContentReviewerSubAgent",
    model="gemini-2.5-flash",
    instruction="""You are a strict Marketing Reviewer.
Review the outreach pitch provided by the creator.

CRITICAL INSTRUCTIONS:
1. Score the pitch from 1 to 100 based on persuasiveness, personalization, and brevity.
2. If the score is UNDER 90, provide specific reasons and actionable feedback so the creator can rewrite it.
3. If the score is 90 OR ABOVE, you MUST call the `exit_loop` tool immediately to finalize the process.
""",
    tools=[exit_loop],
    output_schema=PitchEvaluation
)

marketing_content_loop_agent = LoopAgent(
    name="MarketingContentLoopAgent",
    sub_agents=[content_creator_subagent, content_reviewer_subagent],
    max_iterations=4
)

import webbrowser


def open_url(url: str) -> str:
    """
    Use this tool whenever the user asks to open a website, visit a webpage, go to a specific link, or view a property listing in their browser.

    Args:
        url (str): The exact web address to open. MUST be a raw, fully qualified URL starting with 'https://'.
            Do NOT wrap the URL in markdown format (e.g., never send [Google](https://google.com), just send 'https://www.google.com').
            If the user asks to open a known website by its name (e.g., 'Open Zillow' or 'Go to Syntax Realty'),
            you must infer the proper URL and pass the raw web address.
    """
    # Sanitize common LLM URL mistakes
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    url = url.replace("https.", "https://").replace("http.", "http://")

    webbrowser.open(url)
    return f"Successfully opened {url} in the default browser."


async def make_phone_call(phone_number: str) -> str:
    """
    Use this tool whenever the user asks you to call someone, make a phone call, or connect them to a number via audio.

    Args:
        phone_number (str): The phone number to dial. MUST be in strict E.164 format.
            It must begin with a plus sign (+), followed by the country code (e.g., 1 for US/Canada),
            and the subscriber number. You must remove all spaces, dashes, and parentheses.
            Example: If the user says '(248) 890-6977', you MUST pass '+12488906977'.
            If the user does not provide a country code, assume it is US/Canada (+1).
    """
    # Validate strict E.164 format (Starts with '+', followed by 1 to 15 digits)
    if not re.match(r"^\+[1-9]\d{1,14}$", phone_number):
        return (
            f"ERROR: You passed '{phone_number}', which is invalid. "
            "You MUST use strict E.164 format. Do not ask the user for clarification yet. "
            "Instead, immediately fix the format yourself by stripping all spaces, dashes, and parentheses, "
            "ensure it starts with '+' and the country code (e.g., +1), and call this tool again."
        )

    print(f"Calling: {phone_number}")
    await call(phone_number=phone_number)

    # Return success message to the LLM so it knows the tool finished successfully
    return f"Successfully initiated the call to {phone_number}."

# ==============================================================================
# Supervisor Agent — Evelyn (native audio)
# IMPORTANT: When using GOOGLE_API_KEY (not Vertex AI), the native audio model
# name is "gemini-2.5-flash-native-audio-preview-12-2025", NOT
# "gemini-live-2.5-flash-native-audio" (that's the Vertex AI name).
# ==============================================================================

supervisor_evelyn = LlmAgent(
    name="Evelyn",
    model="gemini-2.5-flash-native-audio-preview-12-2025",  # Gemini API key version
    instruction="""You are Evelyn, an elite Real Estate Multi-Agent Supervisor.
Your job is to orchestrate tasks by calling your agent tools. DO NOT attempt to find leads yourself.
If asked, you can also browse the web using the ComputerUseSubAgent.
You can call phone numbers using the make_phone_call tool.

FOLLOW THIS EXACT WORKFLOW:
1. Greet the user and ask what city/location they want FSBO leads for.
2. When the user provides a location, CALL the `LeadGenerationSequentialAgent` tool to fetch enriched leads.
3. Read a brief summary of the discovered leads to the user, and ask them specifically: "Which of these leads would you like me to generate a marketing pitch for?"
4. Once the user selects a lead, CALL the `MarketingContentLoopAgent` tool, passing in the details of the chosen lead.
5. Read the final, perfected marketing pitch out loud to the user.

Maintain a warm, professional, and confident voice. Be concise.
""",
    tools=[
        AgentTool(agent=lead_generation_sequential_agent),
        AgentTool(agent=marketing_content_loop_agent),
        open_url,
        make_phone_call
    ],
)

# ==============================================================================
# RunConfig — speech and modality settings
# ==============================================================================

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

root_agent = supervisor_evelyn