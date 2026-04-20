"""táltos MCP server — exposes Gemini and Grok as tools to Claude Code."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("táltos")

@mcp.tool()
def hello(name: str = "világ") -> str: # No JSON schema by hand. Type hints are the schema.
    """Verify táltos is wired up correctly."""
    return f"hello {name} táltos itt van."

if __name__ == "__main__":
    mcp.run()