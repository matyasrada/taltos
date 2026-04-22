# táltos

minimal multi-model MCP server. exposes gemini and grok as tools to claude code.

## quick start

```bash
git clone https://github.com/matyasrada/taltos.git
cd taltos
uv sync
cp .env.example .env  # fill in your keys
claude mcp add -s user taltos "$PWD/.venv/bin/python" "$PWD/src/taltos/server.py" # for user scope
```

verify:

```bash
claude mcp list  # taltos ✓ Connected
```

## api keys

- **GEMINI_API_KEY** — https://aistudio.google.com/apikey
- **XAI_API_KEY** — https://console.x.ai/

## tools

- **ask_gemini(prompt, model)** : `gemini-2.5-flash` (default) or `gemini-2.5-flash-lite`
- **ask_grok(prompt, model)** : `grok-4-fast-non-reasoning` (default) or `grok-4-fast-reasoning`
- **hello(name)** : hello world

## license

MIT
