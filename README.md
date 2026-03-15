# Setup Instructions
- Use a Python 3.11 interpreter for best compatibility.
- If running on mac, run the `Install Certificates.command`file inside `/Applications/Python 3.11` folder.

# Run Instructions
- In the terminal type `adk web` to launch Web UI.
- Select the `virtual_assistant` from the dropdown menu.
- Turn Mic on to speak with the assistant

### Examples
- You can ask the assistant to make phone calls
- You can ask the assistant to go to facebook.com
- You can ask the assistant `Find me homes for sale by owner in Pontiac Michigan`


### Architecture Disclaimer
*Why do we use a seperate pipeline server instead of Traditional Google ADK AgentTools?*
- The native-audio preview models do not support AgentTool. The work around is to use a non-standard dual-server (FastAPI & `ADK Web` command) 
- So, the Google ADK web server runs on port 8000 while a separate FastAPI pipeline server runs on port 8001.
- Yes, the limitation could've been avoided using `gemini-2.0-flash-live-001`, but the user experience from `gemini-flash-live-2.5-native-audio-preview` is what I preferred.

### Kill SubAgent Server when your done working:
lsof -ti:8000 | xargs kill -9
lsof -ti:8001 | xargs kill -9  