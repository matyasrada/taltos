"""táltos MCP server - exposes Gemini and Grok as tools to Claude Code."""

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from openai import AsyncOpenAI

# loading api keys from repo-root .env regardless of CWD
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# táltos
mcp = FastMCP("táltos")

gemini = AsyncOpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

grok = AsyncOpenAI(
    api_key=os.environ["XAI_API_KEY"],
    base_url="https://api.x.ai/v1/",
)


@mcp.tool()
async def ask_gemini(
    prompt: str,
    model: Literal[
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ] = "gemini-2.5-flash",
) -> str:
    """Send a prompt to Google Gemini and return its response.
    Defaults to gemini-2.5-flash for general use.
    Use gemini-2.5-flash-lite when the prompt is short/simple and cost matters.
    """
    response = await gemini.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


@mcp.tool()
async def ask_grok(
    prompt: str,
    model: Literal[
        "grok-4-fast-non-reasoning",
        "grok-4-fast-reasoning",
    ] = "grok-4-fast-non-reasoning",
) -> str:
    """Send a prompt to xAI Grok and return its response.
    Defaults to grok-4-fast-non-reasoning (cheapest, fastest) for general use.
    Use grok-4-fast-reasoning when the problem needs step-by-step reasoning.
    """
    response = await grok.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


@mcp.tool()
def hello(name: str = "világ") -> str:  # No JSON schema by hand. Type hints are the schema.
    """Verify táltos is wired up correctly."""
    return f"hello {name} táltos megérkezett."


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
