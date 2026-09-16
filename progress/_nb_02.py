from _write_nb import ROOT, SETUP_CODE, SETUP_COLAB_INSTALL, SETUP_COLAB_SECRETS, SETUP_MD, write

cells = [
    (
        "md",
        """# Module 02: Tools & Custom Tools

This notebook is the **lab**. The lesson is [`outline.md`](outline.md).

**The LLM never sees your source. It sees the schema.** That is the whole module. You will inspect a built-in schema, build a `@tool`, subclass `Tool` with state, run a tool against a real CSV, then give two tools to one agent.

If something fails, [`instructions.md`](instructions.md) has the error table.
""",
    ),
    ("md", SETUP_MD),
    ("code", SETUP_COLAB_INSTALL),
    ("code", SETUP_COLAB_SECRETS),
    ("code", SETUP_CODE),
    (
        "md",
        """## What the model actually sees

A tool is a permissioned function plus four fields. Print them on any tool before you trust an agent with it.

This is the same idea as an OpenAI function spec, an MCP tool list, or a LangChain tool: the model gets a brochure, not the factory.
""",
    ),
    (
        "code",
        r"""from smolagents import CodeAgent, PythonInterpreterTool, Tool, WebSearchTool, tool

python_tool = PythonInterpreterTool()
search_tool = WebSearchTool()

for t in (python_tool, search_tool):
    print("===", type(t).__name__, "===")
    print("name       :", t.name)
    print("description:", t.description[:180].replace("\n", " "), "...")
    print("inputs     :", t.inputs)
    print("output_type:", t.output_type)
    print()
""",
    ),
    (
        "md",
        """`CodeAgent` already has a Python interpreter. `PythonInterpreterTool` is what `ToolCallingAgent` uses when it needs code. `WebSearchTool` is the current search tool (engine=`duckduckgo` by default). We inspect it here; we *use* it in Module 04.
""",
    ),
    (
        "md",
        """## `@tool`: schema from a function

Type hints + a Google-style `Args:` docstring become the schema. No source is sent to the model.

We query the Hub with `pipeline_tag` and `limit=1` so we do not crawl every model.
""",
    ),
    (
        "code",
        r'''import os
from huggingface_hub import list_models

@tool
def top_hf_model(task: str) -> str:
    """Return the most-downloaded Hub model for a pipeline tag.

    Args:
        task: Hugging Face pipeline tag, e.g. 'text-generation' or 'text-classification'.
    """
    token = os.environ.get("HF_TOKEN")
    models = list_models(
        pipeline_tag=task,
        sort="downloads",
        limit=1,
        token=token,
    )
    first = next(iter(models), None)
    if first is None:
        return f"No model found for pipeline_tag={task!r}."
    return first.id

print("name       :", top_hf_model.name)
print("description:", top_hf_model.description)
print("inputs     :", top_hf_model.inputs)
print("output_type:", top_hf_model.output_type)

# Isolation test — no agent yet.
print("direct call:", top_hf_model("text-generation"))
'''
    ),
    (
        "code",
        r"""agent = CodeAgent(tools=[top_hf_model], model=model, max_steps=8)
result = agent.run(
    "What is the most downloaded text-generation model on the Hugging Face Hub? "
    "Use the top_hf_model tool; do not guess from memory."
)
print("\nResult:", result)
print("Steps:", [type(s).__name__ for s in agent.memory.steps])
""",
    ),
    (
        "md",
        """## Subclass `Tool`: schema as class attributes

Use this when you need `__init__` (paths, timeouts, keys). Always call `super().__init__()`. Logic lives in `forward()`.

We run it on the shipped sample CSV — a tool you never execute is not a tool you taught.
""",
    ),
    (
        "code",
        r"""import pandas as pd

class CSVSummaryTool(Tool):
    name = "csv_summary"
    description = (
        "Load a local CSV file and return shape, column names, dtypes, "
        "and numeric describe() stats. Use when the user names a CSV path."
    )
    inputs = {
        "filepath": {
            "type": "string",
            "description": "Path to a CSV file, e.g. 'data/sample_sales.csv'.",
        }
    }
    output_type = "string"

    def __init__(self, max_rows_preview: int = 5):
        super().__init__()
        self.max_rows_preview = max_rows_preview

    def forward(self, filepath: str) -> str:
        path = Path(filepath)
        if not path.is_file():
            return f"File not found: {filepath}"
        df = pd.read_csv(path)
        return (
            f"Shape: {df.shape}\n"
            f"Columns: {list(df.columns)}\n"
            f"Dtypes:\n{df.dtypes.to_string()}\n"
            f"Head:\n{df.head(self.max_rows_preview).to_string()}\n"
            f"Stats:\n{df.describe().to_string()}"
        )

csv_path = ROOT / "data" / "sample_sales.csv"
csv_tool = CSVSummaryTool()
print("schema name:", csv_tool.name)
print("schema inputs:", csv_tool.inputs)
print("--- isolation test ---")
print(csv_tool(str(csv_path)))
""",
    ),
    (
        "code",
        r"""agent = CodeAgent(tools=[csv_tool], model=model, max_steps=8)
result = agent.run(
    f"Summarize the CSV at {csv_path}. How many rows? Which region appears?"
)
print("\nResult:", result)
""",
    ),
    (
        "md",
        """## Schema deep-dive

For `CodeAgent`, smolagents renders your schema as a Python signature + docstring in the system prompt. For `ToolCallingAgent` (next module), the same fields become a JSON function spec.

Either way: **only** `name`, `description`, `inputs`, `output_type` leave your process. Private attributes (`self.timeout`, API keys) do not.

Prefer `"string"` arguments. If you need structure, accept a string and parse it in `forward()`.
""",
    ),
    (
        "code",
        r"""print("CSVSummaryTool.inputs =")
for key, spec in csv_tool.inputs.items():
    print(f"  {key}: {spec}")
""",
    ),
    (
        "md",
        """## Exercises

Test each tool with a direct call before you wrap it in an agent.

**You succeeded if…** is under each TODO. Sample files: `data/sample_sales.csv`, `data/coingecko_sample.json`.
""",
    ),
    (
        "code",
        r"""# TODO Exercise 1: describe_numbers
# Write a @tool named describe_numbers that:
#   - takes numbers: str  (comma-separated, e.g. "1,2,3,4,5")
#   - returns a string with mean, median, and population stdev
#   - does NOT import the statistics library
# Then: isolation-test it, then CodeAgent-ask:
#   "What are the mean, median, and std dev of: 12, 45, 7, 89, 34, 56, 23?"
#
# You succeeded if:
#   - describe_numbers.inputs["numbers"]["description"] is non-empty
#   - a direct call on "1,2,3,4,5" prints mean=3.0, median=3.0
#   - the agent result mentions those three statistics (exact rounding may vary)

# Your code here:
""",
    ),
    (
        "code",
        r"""# TODO Exercise 2: CryptoPriceTool
# Subclass Tool:
#   name = "crypto_price"
#   input coin_id: str  (e.g. "bitcoin", "ethereum", "solana")
#   GET https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd
#   return "bitcoin: $96420 USD" (format flexibly)
# On timeout / 429 / missing id: load data/coingecko_sample.json and use that,
# or return a clear error string. Never raise into the agent loop for expected HTTP failures.
# Call super().__init__().
#
# You succeeded if:
#   - CryptoPriceTool().forward("ethereum") returns a string containing "ethereum" and a dollar amount
#   - a bogus id returns a string (not an exception)
#   - an agent asked for ethereum's price calls your tool (check memory.steps)

# Your code here:
""",
    ),
    (
        "code",
        r"""# TODO Exercise 3: both tools on one agent
# CodeAgent(tools=[describe_numbers, crypto_tool], model=model)
# Task: "What is the mean and std dev of [3, 7, 1, 9, 4, 6]? Also, what is the current price of ethereum?"
# Print how many steps it took and whether both tools appear in the trace.
#
# You succeeded if:
#   - the result mentions both a stats summary and an ethereum price
#   - you can point to two different tool names in the ActionSteps

# Your code here:
""",
    ),
    (
        "md",
        """## Hints (stay out until you have tried)

<details>
<summary>Exercise 1 — stdev by hand</summary>

Population stdev: `sqrt(sum((x - mean)**2) / n)`. Median: sort, then middle or average of two middles.

</details>

<details>
<summary>Exercise 2 — fallback</summary>

```python
import json, requests

class CryptoPriceTool(Tool):
    name = "crypto_price"
    ...
    def __init__(self, fixture_path: str, timeout: float = 8.0):
        super().__init__()
        self.fixture_path = Path(fixture_path)
        self.timeout = timeout

    def forward(self, coin_id: str) -> str:
        coin_id = coin_id.lower().strip()
        try:
            r = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": coin_id, "vs_currencies": "usd"},
                timeout=self.timeout,
            )
            r.raise_for_status()
            price = r.json()[coin_id]["usd"]
        except Exception:
            data = json.loads(self.fixture_path.read_text())
            if coin_id not in data:
                return f"unknown coin_id: {coin_id}"
            price = data[coin_id]["usd"]
        return f"{coin_id}: ${price} USD"
```

</details>
""",
    ),
    (
        "md",
        """## What you built

- A precise picture of a tool: permission + schema, in any framework
- A `@tool` whose docstring *is* the prompt
- A `Tool` subclass with `super().__init__()` and a `forward()` that fails as a string
- A habit: isolation-test, then agent-test, then read the trace

**Key insight:** if the agent ignores your tool, rewrite the brochure (the schema), not the factory (the Python).

---

## Next — Module 03: CodeAgent vs ToolCallingAgent

Same tool, two action languages: Python vs JSON. The schema you just wrote works in both. The traces will not look the same.
""",
    ),
]

write(ROOT / "02_tools_and_custom_tools" / "notebook.ipynb", cells)
