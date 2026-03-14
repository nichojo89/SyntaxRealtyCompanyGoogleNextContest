import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load the .env file from the agent directory
load_dotenv(
    "/Users/jonnichols/Documents/SyntaxRealtyCompanyGoogleNextContest/home_leads_gen_voice_agent/.env"
)

from home_leads_gen_voice_agent.api.pipeline_routes import router

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)