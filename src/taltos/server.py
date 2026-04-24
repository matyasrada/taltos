"""táltos MCP server - exposes Gemini, Grok, and Ollama as tools to Claude Code."""

import asyncio
import os
import sys
from pathlib import Path
from typing import Literal

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from openai import AsyncOpenAI

# loading api keys from repo-root .env regardless of CWD
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# api keys
gemini_api_key = os.getenv("GEMINI_API_KEY")
xai_api_key = os.getenv("XAI_API_KEY")

gemini: AsyncOpenAI | None = None
grok: AsyncOpenAI | None = None

if gemini_api_key:
    gemini = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    print("Gemini client loaded successfully", file=sys.stderr)
else:
    print("GEMINI_API_KEY not found → ask_gemini tool will be disabled", file=sys.stderr)

if xai_api_key:
    grok = AsyncOpenAI(
        api_key=xai_api_key,
        base_url="https://api.x.ai/v1/",
    )
    print("Grok client loaded successfully", file=sys.stderr)
else:
    print("XAI_API_KEY not found → ask_grok tool will be disabled", file=sys.stderr)

# ollama is keyless. probe the local daemon to discover installed models
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
ollama: AsyncOpenAI | None = None
ollama_models: list[str] = []

try:
    _tags = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2.0)
    _tags.raise_for_status()
    ollama_models = [m["name"] for m in _tags.json().get("models", [])]
except Exception as e:
    print(
        f"Ollama not reachable at {OLLAMA_BASE_URL} ({type(e).__name__}) "
        "→ ask_ollama tool will be disabled",
        file=sys.stderr,
    )

if ollama_models:
    ollama = AsyncOpenAI(
        api_key="ollama",  # ignored by the server, but required non-empty by the SDK
        base_url=f"{OLLAMA_BASE_URL}/v1",
    )
    print(
        f"Ollama client loaded ({len(ollama_models)} models: {', '.join(ollama_models)})",
        file=sys.stderr,
    )

if gemini is None and grok is None and ollama is None:
    raise SystemExit("No providers available!\nAdd API keys to .env or start the Ollama daemon.")

# táltos
mcp = FastMCP("táltos")

if gemini is not None:

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


if grok is not None:

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


if ollama is not None:
    OllamaModel = Literal[*ollama_models]
    default_ollama_model = "llama3.2:3b" if "llama3.2:3b" in ollama_models else ollama_models[0]

    @mcp.tool()
    async def ask_ollama(
        prompt: str,
        model: OllamaModel = default_ollama_model,
    ) -> str:
        """Send a prompt to a local Ollama model and return its response.
        Model list is discovered at server startup from the local Ollama daemon.
        Local inference.
        """
        response = await ollama.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


PROVIDERS = []
if gemini is not None:
    PROVIDERS.append(("Gemini", gemini, "gemini-2.5-flash"))
if grok is not None:
    PROVIDERS.append(("Grok", grok, "grok-4-fast-non-reasoning"))
if ollama is not None:
    PROVIDERS.append(("Ollama", ollama, default_ollama_model))

if len(PROVIDERS) >= 2:

    @mcp.tool()
    async def ensemble(prompt: str) -> str:
        """
        Send the same prompt to different models in parallel; return
        each responses labeled. Use when asked to cross-validate a
        claim, compare model perspectives. Costs both API calls.
        """
        tasks = [
            client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            for _, client, model in PROVIDERS
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        def render(label, model, resp):
            if isinstance(resp, Exception):
                return f"## {label} ({model})\n[error: {type(resp).__name__}: {resp}]"
            content = resp.choices[0].message.content or "(empty response)"
            return f"## {label} ({model})\n{content}"

        blocks = [
            render(label, model, resp)
            for (label, _, model), resp in zip(PROVIDERS, results, strict=False)
        ]
        return "\n\n".join(blocks)


@mcp.tool()
def hello(name: str = "világ") -> str:  # No JSON schema by hand. Type hints are the schema.
    """Verify táltos is wired up correctly."""
    return f"hello {name} táltos megérkezett."


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
