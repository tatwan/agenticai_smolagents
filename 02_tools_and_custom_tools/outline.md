# Module 02: Tools & Custom Tools — Outline

---

## 1. What Makes a Good Tool?

### Tool Schema Anatomy

Every tool in smolagents is defined by four fields. These fields are serialized directly into the LLM prompt, so their quality determines whether the agent uses the tool correctly or not at all.

| Field | Type | Purpose |
|---|---|---|
| `name` | `str` | The identifier the LLM writes in generated code to call the tool |
| `description` | `str` | Natural language explanation the LLM reads to decide *when* to use this tool |
| `inputs` | `dict[str, dict]` | A dictionary mapping each parameter name to its type and description |
| `output_type` | `str` | What the LLM should expect back: `"string"`, `"integer"`, `"number"`, `"boolean"`, `"array"`, `"object"`, `"any"` |

### Why Docstring Quality Directly Affects Agent Performance

The LLM receives the tool schema as part of its system prompt. It has no access to your Python source code, no type stubs, and no runtime introspection. The agent's decision logic is:

1. Read the `description` — "Do I need this tool right now?"
2. Read the `inputs` descriptions — "What values should I pass?"
3. Generate code that calls the tool with those values.

If your description is vague (e.g., `"does stuff with data"`), the agent will either skip the tool entirely or call it with wrong arguments. If your input descriptions omit units, formats, or valid value examples, the agent will guess — often incorrectly.

**Practical rules:**
- Write the `description` as if explaining the tool to a junior developer in one paragraph.
- Specify exact input formats in the `inputs` description (e.g., "ISO 8601 date string, e.g. '2024-01-15'").
- State what the return value looks like in the `description` (e.g., "Returns a JSON string containing...").
- Keep descriptions under 200 words — LLM context is finite.

---

## 2. Built-in smolagents Tools

smolagents ships with several ready-to-use tools. These follow the same schema contract as custom tools and can be mixed freely with your own tools.

| Tool Class | `name` | Primary Use |
|---|---|---|
| `PythonInterpreterTool` | `python_interpreter` | Executes arbitrary Python code in a sandboxed subprocess; returns stdout |
| `DuckDuckGoSearchTool` | `web_search` | Runs a DuckDuckGo web search and returns a list of result snippets |
| `VisitWebpageTool` | `visit_webpage` | Fetches the text content of a URL; useful for reading search results |
| `SpeechToTextTool` | `transcriber` | Transcribes audio files using a Whisper-based model on HuggingFace |

### Inspecting a Built-in Tool

Every tool exposes its schema as plain Python attributes. You can inspect them at runtime:

```python
from smolagents import DuckDuckGoSearchTool

tool = DuckDuckGoSearchTool()
print(tool.name)         # "web_search"
print(tool.description)  # multi-line string describing search behavior
print(tool.inputs)       # {'query': {'type': 'string', 'description': '...'}}
print(tool.output_type)  # "string"
```

This is useful for:
- Understanding what the LLM sees when this tool is in its context.
- Debugging why an agent is or is not using a specific tool.
- Copying input schema patterns for your own tools.

---

## 3. The `@tool` Decorator

The `@tool` decorator is the fastest way to turn a plain Python function into a smolagents-compatible tool. smolagents inspects the function's type hints and docstring to auto-generate the tool schema.

### Requirements

1. **Type hints on all parameters** — smolagents reads these to populate the `inputs` schema `"type"` field. Without them, schema generation fails silently and the tool may not be registered.
2. **Return type annotation** — sets `output_type`. Must be one of: `str`, `int`, `float`, `bool`, `list`.
3. **Docstring with an `Args:` section** — smolagents parses Google-style docstrings. Each parameter must appear under `Args:` with its description on the next indented line.

### Docstring Format

```python
@tool
def my_tool(param1: str, param2: int) -> str:
    """
    One-sentence summary of what this tool does.

    Longer optional explanation. Mention what the output looks like.

    Args:
        param1: Description of param1. Include format and examples.
        param2: Description of param2. Specify valid range if applicable.
    """
    ...
```

The first line of the docstring becomes the `description`. The `Args:` section populates the `"description"` sub-field for each input.

### When to Use `@tool` vs Subclassing

Use `@tool` when:
- The tool is a pure function with no state.
- No initialization is required (no API keys to store, no models to load).
- The logic fits cleanly in a single function body.

Use subclassing when the tool needs `__init__`, as described in the next section.

---

## 4. Subclassing `Tool`

When your tool needs to maintain state, load resources at startup, or store credentials, subclass `Tool` directly.

### Class Attribute Contract

Define these four class-level attributes — they serve the same role as the auto-generated schema from `@tool`:

```python
class MyTool(Tool):
    name = "my_tool"
    description = "..."
    inputs = {
        "param": {
            "type": "string",
            "description": "...",
        }
    }
    output_type = "string"
```

### The `__init__` Method

Use `__init__` to accept and store configuration that should not appear in the LLM-visible schema:

```python
def __init__(self, api_key: str):
    super().__init__()
    self.api_key = api_key
```

Always call `super().__init__()`. smolagents performs internal setup in the parent `__init__` that is required for the tool to function.

### The `forward()` Method

All tool logic lives in `forward()`. This method receives the arguments the LLM generates and returns the output. Its signature must match the `inputs` schema keys exactly:

```python
def forward(self, param: str) -> str:
    result = self._call_api(param, key=self.api_key)
    return str(result)
```

### When to Use Subclassing

- Storing an API key or token that is passed at instantiation.
- Loading a heavy model or file once at `__init__` time rather than on every call.
- Splitting complex logic into private helper methods.
- Implementing input validation beyond type checking.

---

## 5. Tool Schema Deep-Dive

### How smolagents Serializes Tools to the LLM Prompt

When you pass tools to an agent, smolagents builds a system prompt that includes each tool's schema. For a `CodeAgent`, the schema appears as a Python function signature with a docstring. For a `ToolCallingAgent`, it is serialized as a JSON object (matching the OpenAI function-calling format).

The serialization reads directly from `name`, `description`, `inputs`, and `output_type`. No other part of your tool code is visible to the LLM.

### Input Type Values

The `"type"` field in each input dict must be one of the following strings:

| Type string | Python equivalent | Notes |
|---|---|---|
| `"string"` | `str` | Most common; use for text, IDs, file paths |
| `"integer"` | `int` | Whole numbers only |
| `"number"` | `float` | Floating-point values |
| `"boolean"` | `bool` | True/False flags |
| `"array"` | `list` | List of items; optionally add `"items"` sub-key |
| `"object"` | `dict` | Nested structure; rarely needed for simple tools |
| `"any"` | any | Escape hatch; avoid unless necessary |

### Nullable Fields

Add `"nullable": true` to an input dict to indicate the parameter is optional. The LLM will still be prompted to provide it, but the schema signals it may be omitted:

```python
inputs = {
    "limit": {
        "type": "integer",
        "description": "Maximum number of results to return. Defaults to 10.",
        "nullable": True,
    }
}
```

### String vs Integer vs Object Types

Prefer `"string"` over `"object"` wherever possible. LLMs generate text natively; constructing valid JSON dicts as arguments is error-prone. If you need structured input, accept a string and parse it inside `forward()`.

---

## 6. Exercises

### Exercise 1: Stats Tool with `@tool`

Write a `@tool`-decorated function called `describe_numbers` that:
- Accepts a single `numbers: str` argument containing comma-separated numeric values (e.g., `"1,2,3,4,5"`).
- Returns a string reporting the mean, median, and standard deviation.
- Does not use the `statistics` library — compute manually using `sum()`, `len()`, and sorted lists.

Then create a `CodeAgent` with this tool and ask: "What are the mean, median, and std dev of: 12, 45, 7, 89, 34, 56, 23?"

Learning goal: practice the `@tool` pattern including type hints and docstring format.

### Exercise 2: CryptoPriceTool Subclass

Create a `Tool` subclass called `CryptoPriceTool` that:
- Has `name = "crypto_price"`.
- Accepts a `coin_id: str` argument (e.g., `"bitcoin"`, `"ethereum"`, `"solana"`).
- Calls the free CoinGecko API: `https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd`
- Returns a formatted string such as `"bitcoin: $67,234 USD"`.
- Handles errors gracefully — coin not found, API timeout, unexpected response shape.

Learning goal: practice the subclass pattern with a real HTTP dependency.

### Exercise 3: Combined Agent

Combine both tools from Exercises 1 and 2 into a single `CodeAgent`. Ask it:

> "What is the mean and std dev of [3, 7, 1, 9, 4, 6]? Also, what is the current price of ethereum?"

Observe whether the agent calls both tools, and in what order. Print the number of steps taken from the agent's run log.

Learning goal: understand how the agent selects among multiple tools based on schema descriptions.

---

## 7. Summary and Module 03 Preview

### Summary

This module covered the complete lifecycle of a smolagents tool:

- The **tool schema** (`name`, `description`, `inputs`, `output_type`) is what the LLM sees — nothing else.
- The **`@tool` decorator** auto-generates a schema from type hints and a Google-style docstring. Use it for stateless functions.
- **Subclassing `Tool`** gives you `__init__` for stateful setup and `forward()` for tool logic. Use it for tools that need API keys, loaded models, or helper methods.
- **Input descriptions and type strings** directly control how accurately the agent calls your tool. Investing time in good descriptions pays off immediately in agent reliability.

### Module 03 Preview: CodeAgent vs ToolCallingAgent

You have been using `CodeAgent` throughout this module. In Module 03, you will meet `ToolCallingAgent` — a fundamentally different reasoning architecture:

- `CodeAgent` generates Python code and executes it. Tools are called as Python functions within that code.
- `ToolCallingAgent` generates structured JSON tool calls, one at a time, following the OpenAI function-calling format.

You will run the same task with both agent types, compare their outputs and step counts, and learn exactly when to prefer one over the other. The module ends with a two-line demonstration of swapping the HuggingFace `InferenceClientModel` for an OpenAI-compatible model.
