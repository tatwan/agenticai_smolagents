# Module 02: Tools & Custom Tools

## Learning Objectives

By the end of this module you will be able to:

1. **Inspect built-in smolagents tools** — read `.name`, `.description`, `.inputs`, and `.output_type` to understand what the LLM receives in its context window.
2. **Write a `@tool`-decorated function** — apply correct type hints and a properly formatted docstring so smolagents auto-generates a valid tool schema.
3. **Subclass `Tool` for stateful tools** — implement `__init__` to store API keys or load resources, and `forward()` to hold tool logic.
4. **Understand the tool schema** — explain what `name`, `description`, `inputs`, and `output_type` map to in the LLM prompt, and why input descriptions determine agent reliability.
5. **Integrate custom tools into a `CodeAgent`** — pass a list of tool instances to `CodeAgent(tools=[...])` and verify the agent uses them correctly.

---

## Prerequisites

- Module 01 complete (you have run the foundations notebook end to end).
- `HF_TOKEN` environment variable set in your `.env` file.
- `uv` installed and the project virtual environment created (see the root `README.md`).

---

## Estimated Time

60–75 minutes

---

## How to Run

From the repository root:

```bash
uv run jupyter lab 02_tools_and_custom_tools/notebook.ipynb
```

Run cells top to bottom. Cells marked `# TODO` are exercises — do not skip them; they build on each other in Exercise 3.

---

## Common Errors

### 1. Missing type hints on a `@tool` function

**Symptom:** The tool is passed to `CodeAgent` but the agent never calls it, or raises a `KeyError` when schema generation runs.

**Cause:** smolagents reads Python type annotations to populate the `inputs[param]["type"]` field. Without annotations, the schema is incomplete and the tool may be silently dropped.

**Fix:** Annotate every parameter and the return type:

```python
# Wrong
@tool
def my_tool(query):
    ...

# Correct
@tool
def my_tool(query: str) -> str:
    ...
```

---

### 2. Wrong docstring format

**Symptom:** `tool.inputs` shows empty descriptions, or smolagents raises a parsing error.

**Cause:** smolagents expects a Google-style docstring with an `Args:` section. Each parameter must be on its own indented line under `Args:`.

**Fix:** Use this exact format:

```python
@tool
def my_tool(query: str, limit: int) -> str:
    """
    One-line summary of the tool.

    Args:
        query: The search string. Use plain English.
        limit: Maximum number of results to return. Must be between 1 and 50.
    """
    ...
```

Note: the `Args:` keyword, the colon after each parameter name, and the indentation are all required.

---

### 3. Tool name collision

**Symptom:** Only one of two similarly-named tools appears in the agent's tool list, or the agent raises a duplicate key error.

**Cause:** Two tools share the same `name` attribute. smolagents uses `name` as a unique key when building the prompt.

**Fix:** Ensure every tool in your `tools=[...]` list has a distinct `name`. For `@tool` functions the name defaults to the function name (underscores preserved). For subclasses, set `name = "..."` explicitly as a class attribute.

---

### 4. `huggingface_hub` not returning results

**Symptom:** `list_models(...)` returns an empty iterator or raises an HTTP error in the `top_hf_model` tool.

**Cause:** Network issue or the HuggingFace Hub API is rate-limiting unauthenticated requests.

**Fix:**
- Ensure `HF_TOKEN` is set in your `.env` file and `load_dotenv()` has been called.
- Pass the token explicitly: `list_models(filter=task, sort="downloads", direction=-1, token=os.environ["HF_TOKEN"])`.
- If you are behind a proxy, set `HTTPS_PROXY` in your environment.

---

## Pro Tips

- **Test tools directly before passing them to an agent.** Call `my_tool("some input")` in a notebook cell and verify the output is what you expect. Debugging a bad tool inside an agent loop is much harder than debugging it in isolation.

- **Keep tool descriptions under 200 words.** Every tool description is injected into the LLM's system prompt. Long descriptions consume context and can push out other important instructions. Be precise, not exhaustive.

- **Put format examples in your input descriptions.** Instead of `"The date to query"`, write `"The date to query in ISO 8601 format, e.g. '2024-01-15'"`. The LLM will follow the example.

- **Return strings whenever possible.** Even if your tool computes a number, returning a formatted string (e.g., `"42.7 degrees Celsius"`) reduces the chance of type coercion errors in the agent's generated code.

- **Use `super().__init__()` in subclass `__init__`.** Omitting this call skips internal smolagents setup and will cause obscure failures at runtime.
