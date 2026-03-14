from home_leads_gen_voice_agent.api.pipeline_routes import router as pipeline_router

def register_routes(app):
    app.include_router(pipeline_router)