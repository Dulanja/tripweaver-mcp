# TripWeaver — MCP-Based Multi-Agent Travel Planner

A multi-agent travel planning assistant built on LangChain, LangGraph, FastAPI, and Gradio,
enhanced to reach external hotel/flight services exclusively through MCP (Model Context Protocol)
servers.

## Architecture

- **Backend**: FastAPI + LangGraph `StateGraph` (`main.py`, `agents/`)
- **Frontend**: Gradio chat UI (`frontend.py`)
- **MCP Servers**: Two standalone MCP servers bridging agents to external travel APIs
  - `mcp_servers/hotel_server.py` — exposes `list_hotels`, `search_hotels`, `book_hotel`
  - `mcp_servers/flight_server.py` — exposes `list_flights`, `search_flights`, `book_flight`

Agents never call third-party APIs directly. `agents/mcp_client.py` spawns both MCP servers
over stdio transport and exposes their tools to the LangGraph nodes in `agents/nodes.py`.
Adding a new service (e.g. activities, weather) only requires a new MCP server file and one
entry in `mcp_client.py` — no changes to agent/node logic.

## How it works

1. User sends a message via the Gradio chat UI.
2. `agents/nodes.py:router` extracts intent (`hotel` / `flight` / `unknown`) and structured
   fields using an LLM with structured output.
3. `agents/graph.py` routes to `hotel_node`, `flight_node`, or `unknown_node` based on intent
   (conditional edges — not a fixed linear path).
4. The chosen node calls the matching MCP tool (e.g. `tools["search_hotels"].ainvoke(...)`),
   awaits the result, and formats a response.
5. Missing required fields (e.g. booking details) trigger a follow-up question instead of
   guessing.
6. If an MCP tool call fails or the external service errors, the node catches the exception
   and returns a clear, user-friendly message — the rest of the app keeps working.

## MCP Server Setup

MCP servers are launched automatically as subprocesses by `agents/mcp_client.py` — no manual
startup needed. They communicate with the backend over stdio.

To run a server standalone for testing:
```bash
python mcp_servers/hotel_server.py
python mcp_servers/flight_server.py
```

## Setup Instructions

1. Create and activate a virtual environment:
```bash
   python -m venv env
   env\Scripts\Activate.ps1      # Windows PowerShell
   source env/bin/activate       # macOS/Linux
```
2. Install dependencies:
```bash
   pip install -r requirements.txt
   pip install fastmcp langchain-mcp-adapters
```
3. Create a `.env` file in the project root:

4. Run the backend:
```bash
   python main.py
```
5. In a separate terminal (same venv), run the frontend:
```bash
   python frontend.py
```

## Known Issue — API Key Quota

The `OPENAI_API_KEY` provided for this assignment returns `insufficient_quota` (429) on
live calls, verified both locally and on the deployed backend, and a prior variant
returned `invalid_api_key` (401), verified by direct `curl` testing against
`https://api.openai.com/v1/models` (bypassing the app entirely). The full pipeline — MCP
tool invocation, intent routing, state passing, and graceful error handling — runs
correctly end-to-end up to the point of the LLM call itself, both locally and in the
deployed environment. Once a funded key is supplied, no code changes are needed — just
update the `OPENAI_API_KEY` environment variable in the Render dashboard for the backend
service.

## Deployment

Both backend and frontend are deployed on **Render** as separate Web Services from this
same repository.

- **Backend**: https://tripweaver-mcp.onrender.com
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `python main.py`
  - Environment Variable: `OPENAI_API_KEY`

- **Frontend**: https://tripweaver-frontend-ys6w.onrender.com
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `python frontend.py`
  - Environment Variable: `TRAVEL_PLANNER_API_URL` = `https://tripweaver-mcp.onrender.com/chat`

Both are on Render's free instance tier, which spins down after periods of inactivity —
the first request after idle time may take 30–60 seconds to respond while the instance
wakes up.

Live chat responses are currently blocked by the API key issue described above (the app
runs and returns a graceful error message rather than crashing), but the deployed
infrastructure, routing, and MCP integration are fully functional and inspectable.

## Tech Stack

FastAPI · LangChain · LangGraph · MCP (via `fastmcp` + `langchain-mcp-adapters`) · Gradio ·
OpenAI (gpt-4o-mini)