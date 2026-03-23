# Context-Hub-Implementation-in-Python

<img width="1410" height="880" alt="image" src="https://github.com/user-attachments/assets/620f9c36-23ed-4dfa-bc05-a2143a16d490" />

This is a minimal agent built with **LangGraph** and **GPT-4o-mini** that fetches up-to-date API documentation from [Context Hub (chub)](https://github.com/anthropics/context-hub) before making the api calls to open ai — so it always works with current, accurate API knowledge instead of stale training data.

1. **`fetch_docs_node`** — checks the in-memory cache, then calls the `chub` CLI to fetch the latest docs for the requested API. Stores the result in LangGraph agent state.
2. **`chatbot_node`** — passes the fetched docs as a system message alongside the user's prompt to GPT-4o-mini.

---

## Project Structure

```
├── main.py       # LangGraph graph definition and agent runner
├── tool.py       # LangChain tool wrapping the chub CLI
├── .env          # API keys (not committed)
└── README.md
```

---

## Prerequisites

- Python 3.10+
- Node.js (required for `chub`)
- An OpenAI API key

## Installation

### 1. Install chub

```bash
npm install chub
```

### 2. Clone and install Python dependencies

```bash
git clone <your-repo-url>
cd <your-repo>
pip install langchain langchain-openai langgraph python-dotenv
```

### 3. Set up environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Update the chub path

In `tool.py`, update `CHUB_PATH` to point to your local chub installation:

```python
CHUB_PATH = r"path\to\node_modules\.bin\chub.cmd"  # Windows
# or
CHUB_PATH = "path/to/node_modules/.bin/chub"        # Mac/Linux
```

> **Tip:** Add `CHUB_PATH` to your `.env` file to avoid hardcoding it.

---

## Usage

### Run the agent

```bash
python main.py
```

### Use it programmatically

```python
from main import run_agent

# Single turn
state = run_agent("How do I make a chat completion call?", api_name="openai")
print(state["messages"][-1].content)

# Multi-turn (docs are reused across turns)
state = run_agent("How do I make a chat completion call?", api_name="openai")
state = run_agent("What about streaming?", api_name="openai", session_state=state)
```

---

## Supported APIs

Context Hub has 68+ providers in its registry. Some examples:

| API | chub ID |
|-----|---------|
| OpenAI Chat | `openai/chat` |
| Anthropic | `anthropic` |
| Stripe | `stripe/api` |
| Supabase | `supabase` |
| Firebase | `firebase` |
| AWS | `aws` |

To add a new alias, update `API_ALIASES` in `tool.py`:

```python
API_ALIASES = {
    "openai": "openai/chat",
    "stripe": "stripe/api",
    # add more here
}
```

---

## The Learning Loop

One of Context Hub's most powerful features is **annotations** — local notes that persist across sessions and are automatically injected into future doc fetches.

```bash
# Save a note about an API
chub annotate openai/chat "Use the responses API for new projects, not chat completions"

# Next time your agent fetches openai/chat docs, this note is included automatically
```

This means your agent gets smarter about APIs over time — without any fine-tuning.

---

## Built With

- [LangGraph](https://github.com/langchain-ai/langgraph) — agent graph framework
- [LangChain](https://github.com/langchain-ai/langchain) — LLM tooling
- [Context Hub](https://github.com/anthropics/context-hub) — up-to-date API docs for agents
- [GPT-4o-mini](https://platform.openai.com/docs/models) — language model

---

## License

MIT
