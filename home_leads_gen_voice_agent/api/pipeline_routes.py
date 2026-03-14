import asyncio
from fastapi import APIRouter
from pydantic import BaseModel

from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types as genai_types

from home_leads_gen_voice_agent.models.LeadTextRequest import LeadTextRequest
from home_leads_gen_voice_agent.prompts import (
    lead_generation_prompt,
    lead_details_prompt,
    create_text_message_prompt,
    evaluate_text_message_prompt
)
from home_leads_gen_voice_agent.models.PropertyForSale import PropertyDetailsList

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

SUBAGENT_MODEL = "gemini-2.5-flash"


class LeadGenRequest(BaseModel):
    location: str
    criteria: str


async def _run_agent(agent, message: str) -> str:
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    session = await session_service.create_session(app_name=agent.name, user_id="evelyn")

    user_message = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=message)]
    )

    result_parts = []
    async for event in runner.run_async(
        user_id="evelyn",
        session_id=session.id,
        new_message=user_message
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    result_parts.append(part.text)

    return "\n".join(result_parts) if result_parts else "No results returned."


@router.post("/lead-generation")
async def lead_generation(request: LeadGenRequest):
    lead_gen_subagent = LlmAgent(
        name="LeadGenerationSubAgent",
        model=SUBAGENT_MODEL,
        instruction=lead_generation_prompt.prompt,
        tools=[google_search],
        output_key="for_sale_by_owner_lead_listings"  # populate session state for next agent
    )

    lead_extraction_subagent = LlmAgent(
        name="LeadExtractionSubAgent",
        model=SUBAGENT_MODEL,
        instruction=lead_details_prompt.prompt,
        # reads {for_sale_by_owner_lead_listings} from session state via prompt template
    )
    sequential_agent = SequentialAgent(
        name="LeadGenerationSequentialAgent",
        sub_agents=[lead_gen_subagent, lead_extraction_subagent]
    )

    result = await _run_agent(
        sequential_agent,
        f"Find homes for sale in {request.location}. Criteria: {request.criteria}"
    )
    return {"result": result}


@router.post("/marketing-content")
async def marketing_content(request: LeadTextRequest):
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
    )
    loop_agent = LoopAgent(
        name="MarketingContentLoopAgent",
        sub_agents=[content_creator_subagent, content_reviewer_subagent],
        max_iterations=4
    )

    result = await _run_agent(
        loop_agent,
        f"Create a text message pitch for this property: {request.model_dump_json()}"
    )
    return {"result": result}