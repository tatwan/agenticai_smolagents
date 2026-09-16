# Module 02: Tools & Custom Tools

**Read this first**, then run `notebook.ipynb`.

**Time:** 75–90 minutes · **Depends on:** Module 01 (`CodeAgent`, `memory.steps`, a working model)

---

## 1. What is a tool?

In every agent stack, a **tool** is a function the harness is willing to run when the model asks.

That is a narrower idea than “anything the model might do.” The model cannot:

- open your laptop’s files unless you wrap that in a tool
- hit CoinGecko unless you wrap that in a tool
- see your Python source unless you paste it into the prompt (please do not)

The model **can** read a short description of the function and guess arguments. That description is the **schema**.

```
You (engineer)                 Harness                      Model
─────────────────              ──────────                   ─────
write Python                   expose schema in             read schema
implement forward()    →       the system prompt     →      choose name + args
return a string                execute, capture             never see source
                               observation
```

This split is not a smolagents quirk. OpenAI function-calling, Anthropic tools, MCP servers, LangChain tools, and a JSON blob you stuff into a system prompt all do the same thing: **the LLM only sees the contract.**

**The sentence to keep:** *The LLM never sees your source. It sees the schema.*

If the agent misuses a tool, the first suspect is the schema, not the model.

---

## 2. When to wrap something as a tool

| Situation | Tool? | Why |
|---|---|---|
| Deterministic math you already know how to write | Maybe | A tool is more reliable than hoping the model arithmetic is right. CodeAgent can also just write the math. |
| Live data (prices, weather, tickets) | Yes | Weights are stale. |
| Privileged actions (send email, drop a table) | Yes, and lock the schema down | You want an allow-list, not a Python interpreter. |
| “Think harder about this paragraph” | No | That is another model call, not a tool. |
| One-off notebook experiment | No | Call the function yourself. |

A tool is a **permission and a promise**: “the model may call this, with these arguments, and I will return something shaped like this.”

Too many tools → the model picks the wrong one. Too-vague descriptions → the model invents arguments. This is why production agents often have **fewer, sharper** tools than demo agents.

---

## 3. How a schema is shaped (any framework)

Four fields. Names vary (`parameters` vs `inputs`, `returns` vs `output_type`). The job does not.

| Field | Job | Failure mode if sloppy |
|---|---|---|
| `name` | The identifier the model will write | Collisions; the model calls `search` when you meant `search_docs` |
| `description` | **When** to use it | Unused tool, or used on every turn |
| `inputs` | Names, types, formats, examples | Wrong types, missing units, hallucinated keys |
| `output_type` / returns | What comes back | The model parses a number as a sentence or vice versa |

Write the description as if briefing a competent intern who cannot see the building:

- One sentence: what it does
- What the arguments look like (`ISO 8601 date, e.g. 2026-09-16`)
- What success looks like (`"bitcoin: $96420 USD"`)
- What failure looks like (`"unknown coin_id: xyz"`)

Keep it under ~200 words. Schema is prompt. Prompt is budget.

---

## 4. How smolagents implements this

### Inspect before you invent

Every `Tool` instance has `.name`, `.description`, `.inputs`, `.output_type`. Print them. That is **exactly** what the model will see.

Built-ins worth knowing (smolagents 1.26):

| Class | Typical `name` | Notes |
|---|---|---|
| `PythonInterpreterTool` | `python_interpreter` | Used by `ToolCallingAgent` when it needs code. `CodeAgent` already has an interpreter. |
| `WebSearchTool` | `web_search` | Default engine `duckduckgo`; also `bing`, `exa`. Module 04. |
| `DuckDuckGoSearchTool` | `web_search` | Still exists; talks to the `ddgs` package. Prefer `WebSearchTool` in new code. |
| `VisitWebpageTool` | `visit_webpage` | HTML → markdown, truncated. |
| `FinalAnswerTool` | `final_answer` | Always present. This is how the loop stops. |

### Two ways to build your own

**`@tool` on a function** — no state, no `__init__`. smolagents reads type hints + a Google-style `Args:` docstring and builds the schema.

```python
@tool
def describe_numbers(numbers: str) -> str:
    """Return mean and median for a comma-separated list of numbers.

    Args:
        numbers: Comma-separated floats, e.g. '3, 7, 1.5'.
    """
    ...
```

Requirements: hints on **every** parameter and the return type; `Args:` with one line per parameter. Miss either, and the schema is wrong in a way that is annoying to debug inside an agent loop.

**Subclass `Tool`** — when you need state (API keys, a loaded file, a session).

```python
class CryptoPriceTool(Tool):
    name = "crypto_price"
    description = "..."
    inputs = {"coin_id": {"type": "string", "description": "..."}}
    output_type = "string"

    def __init__(self, timeout: float = 10.0):
        super().__init__()          # required
        self.timeout = timeout

    def forward(self, coin_id: str) -> str:
        ...
```

`forward()` is the only method the harness calls. Its argument names must match `inputs` keys.

Use `@tool` until you need `__init__`. Then subclass. That rule travels: decorator vs class is how most libraries split “pure function” from “configured client.”

### Input type strings

`"string"` | `"integer"` | `"number"` | `"boolean"` | `"array"` | `"object"` | `"any"`

Prefer `"string"` over `"object"`. Models emit text. Nested JSON arguments fail more often than a string you parse yourself.

Optional parameters: `"nullable": true` plus a default inside `forward()`.

---

## 5. How to test (before you give it to an agent)

1. **Call the tool as a Python object.** `csv_tool("data/sample_sales.csv")` should print something you would be happy to feed a model.
2. **Print the schema.** If you would not know when to use it, neither will the model.
3. **Then** pass it into `CodeAgent(tools=[...])` and ask a question that *requires* the tool.
4. Read `memory.steps`. Did it call your tool, or did it invent an answer from weights?

If step 4 shows no tool call, your description did not match the question. Fix the schema, not the prompt first.

---

## 6. Safety, still

A tool is code **you** run with arguments **the model** chose.

- Validate and constrain (`coin_id` allow-list, path confined to a data directory).
- Time out HTTP.
- Return error **strings**, not exceptions, when the failure is expected (unknown id, 404). Exceptions abort the hop; strings become observations the model can recover from.
- Never put secrets in the schema. Pass them in `__init__` from the environment.

---

## 7. Exercises

1. `@tool describe_numbers` — mean, median, stdev by hand; comma-separated string in.
2. `CryptoPriceTool` — CoinGecko, with a local JSON fallback when the network 429s.
3. Combine both in one agent.

Success criteria live next to the `# TODO` cells. Sample data: `data/sample_sales.csv`.

---

## 8. What you should be able to say out loud

- A tool is a permissioned function plus a schema. The model only sees the schema.
- I test tools in isolation before I wrap them in an agent.
- `@tool` for pure functions; `Tool` + `forward()` when I need state.
- Vague descriptions are the main reason agents “don’t use my tool.”

**Next — Module 03.** Same tool, two loops: the model writes Python vs the model writes JSON. The schema does not change. The action language does.
