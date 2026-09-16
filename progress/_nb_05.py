from _write_nb import ROOT, SETUP_CODE, SETUP_COLAB_INSTALL, SETUP_COLAB_SECRETS, SETUP_MD, write

cells = [
    (
        "md",
        """# Module 05: Multi-Agent Orchestration

This notebook is the **lab**. The lesson is [`outline.md`](outline.md).

**Descriptions are the manager’s routing table.** There is no separate `ManagedAgent` class in current smolagents: set `name` and `description` on each specialist, pass them in `managed_agents=`.

We keep the analyst on **local CSV** so the module still teaches if search flakes.

Errors: [`instructions.md`](instructions.md).
""",
    ),
    ("md", SETUP_MD),
    ("code", SETUP_COLAB_INSTALL),
    ("code", SETUP_COLAB_SECRETS),
    ("code", SETUP_CODE),
    (
        "md",
        """## Recap: when *not* to split

If one tool list and one loop would do, do not pay for nested LLM calls. Split when jobs (and blast radii) actually differ: web vs local files, writer vs researcher.
""",
    ),
    (
        "md",
        """## Specialists

The analyst uses the CSV tool from Module 02 (redefined here so this notebook stands alone). The researcher uses Module 04 tools, with a Bing fallback if DuckDuckGo Lite is empty.
""",
    ),
    (
        "code",
        r'''from smolagents import CodeAgent, Tool, ToolCallingAgent, VisitWebpageTool, WebSearchTool
import pandas as pd

class CSVSummaryTool(Tool):
    name = "csv_summary"
    description = (
        "Load a local CSV and return shape, columns, and numeric describe(). "
        "Pass a filesystem path, not a URL."
    )
    inputs = {
        "filepath": {"type": "string", "description": "Local path to a CSV file."}
    }
    output_type = "string"

    def __init__(self):
        super().__init__()

    def forward(self, filepath: str) -> str:
        path = Path(filepath)
        if not path.is_file():
            return f"File not found: {filepath}"
        df = pd.read_csv(path)
        return f"Shape: {df.shape}\nColumns: {list(df.columns)}\n{df.describe().to_string()}"

csv_path = ROOT / "data" / "sample_sales.csv"
csv_tool = CSVSummaryTool()
print(csv_tool(str(csv_path))[:400])

try:
    search = WebSearchTool(max_results=5, engine="duckduckgo")
    search("smolagents")
except Exception:
    search = WebSearchTool(max_results=5, engine="bing")
visit = VisitWebpageTool(max_output_length=8000)
print("search engine:", search.engine)
''',
    ),
    (
        "code",
        r'''data_analyst = CodeAgent(
    tools=[csv_tool],
    model=model,
    name="data_analyst",
    description=(
        "Analyzes a local CSV. Pass the file path AND a specific numeric question "
        "(e.g. 'total units in sample_sales.csv'). Returns figures, not essays. "
        "Do not send this agent web URLs."
    ),
    max_steps=5,
)

web_researcher = CodeAgent(
    tools=[search, visit],
    model=model,
    name="web_researcher",
    description=(
        "Searches the web and visits pages for current public facts. "
        "Pass one specific question. Returns a short answer with a source URL. "
        "Do not send this agent local file paths."
    ),
    max_steps=6,
)

print("analyst:", data_analyst.name)
print("researcher:", web_researcher.name)
''',
    ),
    (
        "md",
        """## Manager with no tools of its own
""",
    ),
    (
        "code",
        r'''manager = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[data_analyst, web_researcher],
    max_steps=10,
)

print("managed_agents is a dict:", type(manager.managed_agents))
print("names:", list(manager.managed_agents))
for agent in manager.managed_agents.values():
    print(f"- {agent.name}: {agent.description[:80]}...")
''',
    ),
    (
        "code",
        r'''combined = manager.run(
    f"Two jobs. (1) Using the local CSV at {csv_path}, how many rows and what "
    f"are the unique regions? Delegate numbers to data_analyst. "
    f"(2) In one sentence, what is Hugging Face smolagents? Delegate to "
    f"web_researcher and require a source URL."
)
print(combined)
print("manager steps:", [type(s).__name__ for s in manager.memory.steps])
''',
    ),
    (
        "md",
        """## Did the manager actually delegate?

Look for tool names equal to specialist names. If web search failed, you should still see `data_analyst`.
""",
    ),
    (
        "code",
        r'''for i, step in enumerate(manager.memory.steps):
    calls = getattr(step, "tool_calls", None)
    if calls:
        print(i, calls)

print("\nSanity check: sample_sales.csv has 12 data rows, regions east/north/south/west.")
print("If the analyst said 1000 rows, it ignored csv_summary. Open data_analyst.memory.steps.")
''',
    ),
    (
        "md",
        """## Exercises
""",
    ),
    (
        "code",
        r'''# TODO Exercise 1: add report_writer
# CodeAgent with tools=[], name="report_writer",
# description: formats a markdown report with sections Summary / Findings / Numbers.
# Pass it into a NEW manager with the two existing specialists + this one.
# Task: research smolagents in one sentence, analyze sample_sales.csv row count,
# then have report_writer format both.
#
# You succeeded if:
#   - list(manager.managed_agents) has three names
#   - the manager trace shows report_writer (or you explain why it skipped)
#   - the final answer looks like markdown with headings, not a single blob

# Your code here:
''',
    ),
    (
        "code",
        r'''# TODO Exercise 2: local pipeline (fallback-first)
# Manager + data_analyst only is enough to pass.
# Task: from data/sample_sales.csv, which product has the highest total units?
# Stretch: add web_researcher to find a *public* CSV URL on the same theme;
# if download fails, still answer from the local file and say so.
#
# You succeeded if:
#   - the numeric answer comes from the local CSV (compute it yourself to check)
#   - the manager passed a path string, not a pandas object
#   - you did not require a live download to finish the exercise

# Your code here:
''',
    ),
    (
        "md",
        """## Hints

<details>
<summary>Highest units product</summary>

Group `units` by `product` in the CSV: widget should win on the shipped sample (12+3+9+20+14 = 58).

</details>

<details>
<summary>report_writer description</summary>

“Formats text only. Pass the already-gathered facts as the task string. Returns markdown. Does not search or read files.”

</details>
""",
    ),
    (
        "md",
        """## What you built

- A manager that routes on specialist **descriptions**
- Mixed agent types (code analyst, web researcher)
- A local-first path so multi-agent is learnable even when the web is rude

**Key insight:** adding agents is cheap in code and expensive in tokens. Split jobs, not ego.

---

## Next — Module 06: Observability

Same prompt, different traces. You will log params, metrics, and steps — first by hand, then with `mlflow.smolagents.autolog()`.
""",
    ),
]

write(ROOT / "05_multi_agent_orchestration" / "notebook.ipynb", cells)
