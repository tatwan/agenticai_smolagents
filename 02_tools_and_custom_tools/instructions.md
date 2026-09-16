# Module 02: Tools & Custom Tools — how to run this lab

**Module:** 02 of 06  
**Read first:** [`outline.md`](outline.md)  
**Then run:** [`notebook.ipynb`](notebook.ipynb)

---

## Learning objectives

- Inspect a tool schema (`.name`, `.description`, `.inputs`, `.output_type`) and explain that this is all the model sees
- Write a `@tool` function with type hints and a Google-style `Args:` docstring
- Subclass `Tool`, call `super().__init__()`, and implement `forward()`
- Test a tool as a plain Python object before handing it to an agent
- Run a `CodeAgent` with more than one custom tool

---

## Prerequisites

- Module 01 complete
- Same environment as the README: `uv sync`, `.env` at the repo root
- Sample CSV at `data/sample_sales.csv` (shipped with the repo)

---

## Estimated time

75–90 minutes

---

## How to run

From the repository root:

```bash
uv run jupyter lab 02_tools_and_custom_tools/notebook.ipynb
```

Run top to bottom. Exercise 3 reuses tools from exercises 1 and 2.

---

## Common errors

### 1. Missing type hints on `@tool`

Symptom: empty `inputs`, or the agent never calls the tool.

Fix: annotate every parameter and the return type (`str`, `int`, `float`, `bool`, `list`).

### 2. Wrong docstring shape

smolagents parses **Google-style** `Args:`. NumPy `Parameters` and Markdown bullets will not fill `.inputs[...]["description"]`.

```python
"""One-line summary.

Args:
    query: Plain-English search string.
    limit: Max results, 1–50.
"""
```

### 3. Forgot `super().__init__()`

Subclass tools then fail in obscure ways during agent setup. Always call it.

### 4. `list_models` is slow or empty

Pass `pipeline_tag=...`, `limit=1`, and `token=os.environ.get("HF_TOKEN")`. Do not iterate the whole Hub. `filter=` still exists but Hub docs prefer `pipeline_tag` for tasks.

### 5. CoinGecko `429` / network error

Expected on the free API. The notebook’s `CryptoPriceTool` should fall back to `data/coingecko_sample.json`. If you wrote your own without a fallback, use that file.

### 6. Agent answers from weights and skips your tool

The question did not match the description, or the tool was not in `tools=[...]`. Print `agent.tools.keys()` (or `list(agent.tools)`) and tighten the description. Then inspect `memory.steps`.

### 7. `FileNotFoundError` for the sample CSV

Working directory is not the repo root. Use a path relative to `course_setup.ROOT` (the notebook does this) or an absolute path to `data/sample_sales.csv`.

---

## Tips

- Call `my_tool("...")` yourself. If that output is garbage, the agent cannot save you.
- Return **strings**, including error strings.
- Put examples in input descriptions (`e.g. 'bitcoin'`).
- Keep descriptions short. Schema is prompt.
