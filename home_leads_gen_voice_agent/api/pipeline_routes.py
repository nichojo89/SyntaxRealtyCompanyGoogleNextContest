from fastapi import APIRouter
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types as genai_types
from home_leads_gen_voice_agent.models.LeadGenRequest import LeadGenRequest
from home_leads_gen_voice_agent.models.LeadTextRequest import LeadTextRequest
from home_leads_gen_voice_agent.prompts import (
    lead_generation_prompt,
    lead_details_prompt,
    create_text_message_prompt,
    evaluate_text_message_prompt
)

router = APIRouter(prefix="/pipeline", tags=["pipeline"])
SUBAGENT_MODEL = "gemini-2.5-flash"

_lead_gen_runner: Runner | None = None
_lead_gen_session_service: InMemorySessionService | None = None

_marketing_runner: Runner | None = None
_marketing_session_service: InMemorySessionService | None = None


def _get_lead_gen_runner() -> tuple[Runner, InMemorySessionService]:
    """
    Singleton that creates lead generation Sequential Agent

    returns: Bot runner and In-Memory session service
    """

    global _lead_gen_runner, _lead_gen_session_service
    if _lead_gen_runner is None:
        lead_gen_subagent = LlmAgent(
            name="LeadGenerationSubAgent",
            model=SUBAGENT_MODEL,
            instruction=lead_generation_prompt.prompt,
            tools=[google_search],
            output_key="for_sale_by_owner_lead_listings"
        )
        lead_extraction_subagent = LlmAgent(
            name="LeadExtractionSubAgent",
            model=SUBAGENT_MODEL,
            instruction=lead_details_prompt.prompt
        )
        sequential_agent = SequentialAgent(
            name="LeadGenerationSequentialAgent",
            sub_agents=[lead_gen_subagent, lead_extraction_subagent]
        )
        _lead_gen_session_service = InMemorySessionService()
        _lead_gen_runner = Runner(
            agent=sequential_agent,
            app_name="LeadGenerationSequentialAgent",
            session_service=_lead_gen_session_service
        )
    return _lead_gen_runner, _lead_gen_session_service


def _get_marketing_runner() -> tuple[Runner, InMemorySessionService]:
    """
    Singleton that creates lead generation Loop Agent

    returns: Bot runner and In-Memory session service
    """

    global _marketing_runner, _marketing_session_service
    if _marketing_runner is None:
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
        _marketing_session_service = InMemorySessionService()
        _marketing_runner = Runner(
            agent=loop_agent,
            app_name="MarketingContentLoopAgent",
            session_service=_marketing_session_service
        )
    return _marketing_runner, _marketing_session_service


async def _run_agent(runner: Runner, session_service: InMemorySessionService, message: str) -> str:
    """
    Runs a bot within In-Memory Session.

    returns: Websocket LLM parts
    """

    session = await session_service.create_session(
        app_name=runner.agent.name,
        user_id="evelyn"
    )
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
    """Http Endpoint that runs Sequential Agent to generate leads"""

    runner, session_service = _get_lead_gen_runner()
    result = await _run_agent(
        runner,
        session_service,
        f"Find homes for sale in {request.location}. Criteria: {request.criteria}"
    )
    return {"result": result}


@router.post("/marketing-content")
async def marketing_content(request: LeadTextRequest):
    """Http Endpoint that runs Loop Agent to generate carefully curated text message content"""

    runner, session_service = _get_marketing_runner()
    result = await _run_agent(
        runner,
        session_service,
        f"Create a text message pitch for this property: {request.model_dump_json()}"
    )
    return {"result": result}