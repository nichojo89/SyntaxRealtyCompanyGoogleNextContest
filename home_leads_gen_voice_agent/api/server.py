from pathlib import Path

import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

# Load the .env_old file on Server
load_dotenv(Path(__file__).parent.parent / ".env_old")

from home_leads_gen_voice_agent.api.pipeline_routes import router

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)