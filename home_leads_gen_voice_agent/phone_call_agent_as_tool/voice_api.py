from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uvicorn

from home_leads_gen_voice_agent.phone_call_agent_as_tool.outbound_bot_runner import call
from home_leads_gen_voice_agent.phone_call_agent_as_tool.models.fsbo_prompt_parameters import FSBOPromptParameters

app = FastAPI(title="Pipecat Voice Worker")


# Define what the incoming HTTP JSON request should look like
class CallRequest(BaseModel):
    phone_number: str
    fsbo_data: dict


@app.post("/start_call")
async def start_call(request: CallRequest, background_tasks: BackgroundTasks):
    try:
        # 1. Convert the incoming dictionary back into your Pydantic model
        fsbo_params = FSBOPromptParameters(**request.fsbo_data)

        # 2. Run the Pipecat WebRTC script in the background
        # This allows the API to return a "200 OK" to Cloud Run instantly without making the LLM wait
        background_tasks.add_task(call, request.phone_number, fsbo_params)

        return {"status": "success", "message": f"Dialing {request.phone_number}..."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, loop="asyncio")