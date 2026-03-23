import subprocess
from langchain_core.tools import tool

docs_cache = {}

CHUB_PATH = r"D:\python_projects\alex_projects\pallet_connect_agent\node_modules\.bin\chub.cmd"

API_ALIASES = {
    "openai": "openai/chat",
    "openai api": "openai/chat",
    "openai/chat": "openai/chat",
}

@tool
def fetch_api_docs(api_name: str) -> str:
    """Fetch up-to-date API documentation from Context Hub."""

    resolved = API_ALIASES.get(api_name.lower(), api_name.lower())

    if resolved in docs_cache:
        return docs_cache[resolved]

    result = subprocess.run(
        [CHUB_PATH, "get", resolved, "--lang", "py"],
        capture_output=True,
        text=True,
        shell=True
    )

    if not result.stdout:
        return f"Could not fetch docs for '{resolved}'. Error: {result.stderr}"

    docs_cache[resolved] = result.stdout
    return result.stdout
