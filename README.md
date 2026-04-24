# táltos

minimal multi-model MCP server. exposes gemini, grok, and ollama as tools to claude code.

## quick start

```bash
git clone https://github.com/matyasrada/taltos.git
cd taltos
uv sync
cp .env.example .env  # fill in your keys
claude mcp add -s user taltos "$PWD/.venv/bin/taltos" # for user scope
```

verify:

```bash
claude mcp list  # taltos ✓ Connected
```

## providers

- **GEMINI_API_KEY** — https://aistudio.google.com/apikey
- **XAI_API_KEY** — https://console.x.ai/
- **Ollama** — keyless; probed at startup from `OLLAMA_BASE_URL` (default `http://localhost:11434`). The model list is discovered once at startup. restart the server after `ollama pull`.

At least one provider must be available or the server exits.

## tools

- **ask_gemini(prompt, model)** : `gemini-2.5-flash` (default) or `gemini-2.5-flash-lite`
- **ask_grok(prompt, model)** : `grok-4-fast-non-reasoning` (default) or `grok-4-fast-reasoning`
- **ask_ollama(prompt, model)** : local inference; model list discovered from the Ollama daemon at startup
- **ensemble(prompt)** : fans the prompt out to every available provider in parallel, returns labeled responses.
- **hello(name)** : hello world

## license

MIT
