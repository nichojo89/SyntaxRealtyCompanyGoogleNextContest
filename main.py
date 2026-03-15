import os
import threading
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app
from home_leads_gen_voice_agent.api.server import app as pipeline_app

agents_dir = os.path.join(os.path.dirname(__file__), ".")

app = get_fast_api_app(
    agents_dir=agents_dir,
    web=True,
    host="0.0.0.0",
    port=8000,
    allow_origins=["*"],
)

def _start_pipeline_server():
    uvicorn.run(pipeline_app, host="0.0.0.0", port=8001, log_level="warning")

thread = threading.Thread(target=_start_pipeline_server, daemon=True)
thread.start()