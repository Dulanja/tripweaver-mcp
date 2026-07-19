import sys
from langchain_mcp_adapters.client import MultiServerMCPClient

mcp_client = MultiServerMCPClient({
    "hotel": {"command": sys.executable, "args": ["mcp_servers/hotel_server.py"], "transport": "stdio"},
    "flight": {"command": sys.executable, "args": ["mcp_servers/flight_server.py"], "transport": "stdio"},
})

_tools_cache = {}


async def get_mcp_tools() -> dict:
    global _tools_cache
    if not _tools_cache:
        tools = await mcp_client.get_tools()
        _tools_cache = {t.name: t for t in tools}
    return _tools_cache