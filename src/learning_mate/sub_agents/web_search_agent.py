import os
from textwrap import dedent

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from ..utils import retry_config


# Check if Tavily API key exists
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    raise RuntimeError(
        "Failed to create MCP session: TAVILY_API_KEY not found. "
        "Please set the TAVILY_API_KEY environment variable."
    )

web_search_agent = Agent(
    model=Gemini(
        model="gemini-2.5-flash-lite",  # Used for speed
        retry_options=retry_config
    ),
    name="web_search_agent",
    description="Agent that retrieves information from the web.",
    instruction=dedent("""
        Retrieve and synthesize accurate, up-to-date, and relevant information from reliable web sources to answer all user queries.
    """),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "tavily-mcp@latest",
                    ],
                ),
                timeout=30,
            ),
        )
    ],
)
