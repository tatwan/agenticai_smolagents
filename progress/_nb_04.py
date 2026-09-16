from _write_nb import ROOT, SETUP_CODE, SETUP_COLAB_INSTALL, SETUP_COLAB_SECRETS, SETUP_MD, write

cells = [
    (
        "md",
        """# Module 04: Web Search & Browsing

This notebook is the **lab**. The lesson is [`outline.md`](outline.md).

Closed weights cannot answer “what shipped this week.” Retrieval can. The web is one retrieval store (alongside your docs, your DB, MCP). Pattern:

**search → select → visit → extract → cite**

We use `WebSearchTool` (current smolagents default) and `VisitWebpageTool`. Isolation-test both before any agent.

This module **will flake**. Rate limits and bot walls are part of the lesson, not a failed install.

Errors: [`instructions.md`](instructions.md).
""",
    ),
    ("md", SETUP_MD),
    ("code", SETUP_COLAB_INSTALL),
    ("code", SETUP_COLAB_SECRETS),
    ("code", SETUP_CODE),
    (
        "md",
        """## Isolation test: search

`engine="duckduckgo"` is the default. Also `"bing"` and `"exa"` (Exa needs `EXA_API_KEY`).
""",
    ),
    (
        "code",
        r'''from smolagents import CodeAgent, ToolCallingAgent, VisitWebpageTool, WebSearchTool

search = WebSearchTool(max_results=5, engine="duckduckgo")
print("schema:", search.name, search.inputs, "engine:", search.engine)

try:
    raw = search("smolagents huggingface documentation")
except Exception as exc:
    print("duckduckgo engine failed:", type(exc).__name__, exc)
    print("Falling back to engine='bing' — this is expected on some networks.")
    search = WebSearchTool(max_results=5, engine="bing")
    raw = search("smolagents huggingface documentation")
print(raw[:1500])
''',
    ),
    (
        "md",
        """## Isolation test: visit

If this returns a CAPTCHA or nearly nothing, the host blocked you. Try another URL. Truncation is normal on long docs.
""",
    ),
    (
        "code",
        r'''visit = VisitWebpageTool(max_output_length=8000)
page = visit("https://huggingface.co/docs/smolagents")
print(page[:1200])
print("\n... length", len(page))
''',
    ),
    (
        "md",
        """## Agent: search only

Useful for “give me links.” Snippets are not the page — notice how little detail you get.
""",
    ),
    (
        "code",
        r'''search_agent = CodeAgent(
    tools=[search],
    model=model,
    max_steps=6,
)
r = search_agent.run(
    "Find the official smolagents documentation URL on Hugging Face. "
    "Return the URL you found in the search results, not one you invent."
)
print(r)
print("steps", [type(s).__name__ for s in search_agent.memory.steps])
''',
    ),
    (
        "md",
        """## Agent: search + visit + cite

The task **requires** a visit and a URL. After it runs, skim `memory.steps` and check the URL actually appeared in an observation.
""",
    ),
    (
        "code",
        r'''research_agent = CodeAgent(
    tools=[search, visit],
    model=model,
    max_steps=8,
)
task = (
    "What is Hugging Face smolagents? Visit the official docs or blog, "
    "extract a one-sentence description, and cite the exact URL you visited. "
    "Only cite a URL that appeared in a tool observation."
)
r = research_agent.run(task)
print(r)
print("steps", [type(s).__name__ for s in research_agent.memory.steps])
''',
    ),
    (
        "code",
        r'''print("Did a visit happen?")
for i, step in enumerate(research_agent.memory.steps):
    calls = getattr(step, "tool_calls", None)
    if calls:
        print(i, calls)
''',
    ),
    (
        "md",
        """## Exercises

Exercise 2 is **stretch**. If search rate-limits you, stop after one source and write what you would change.
""",
    ),
    (
        "code",
        r'''# TODO Exercise 1: latest stable Python
# Agent with WebSearchTool + VisitWebpageTool, max_steps=8.
# Task: latest stable Python release. Prefer python.org. Visit the page.
# Extract the exact version (e.g. 3.13.x). Cite the URL.
#
# You succeeded if:
#   - the result contains a version number that looks like 3.xx
#   - you can point to a visit_webpage (or equivalent) in memory.steps
#     OR you honestly note that the site blocked you and you used snippets
#   - the cited URL also appears in an observation, not only in the final sentence

# Your code here:
''',
    ),
    (
        "code",
        r'''# TODO Exercise 2 (stretch): mini research table
# Same tools, max_steps=10.
# Pick a topic you can verify (default: "dbt data build tool best practices 2025 2026").
# Return a markdown table: Title | One takeaway | URL  (up to 3 rows).
# If you get rate-limited, return 1 row and a sentence on what you would change.
#
# You succeeded if:
#   - at least one row has a URL that appeared in the trace
#   - you did not invent a comparison of 3 articles from snippets alone
#     without saying so

# Your code here:
''',
    ),
    (
        "md",
        """## Hints

<details>
<summary>Exercise 1 prompt shape</summary>

“What is the latest stable Python version? Visit https://www.python.org/downloads/ (or the URL search returns) and extract the version from the page. Cite that URL.”

</details>

<details>
<summary>Rate limited</summary>

`time.sleep(5)` between runs, or `WebSearchTool(engine="bing")`. Do not tight-loop the same query.

</details>
""",
    ),
    (
        "md",
        """## What you built

- A retrieval loop that does not depend on smolagents: search, visit, extract, cite
- Explicit `WebSearchTool` + `VisitWebpageTool` instead of a mystery `add_base_tools`
- A habit of checking that cited URLs existed in observations

**Key insight:** the web is just another tool-shaped store. Snippets are advertisements for pages. Read the page.

---

## Next — Module 05: Multi-agent orchestration

One agent holding search *and* analysis *and* writing will thrash. A manager with named specialists — **descriptions as the routing table** — is the next pattern.
""",
    ),
]

write(ROOT / "04_web_search_and_browsing" / "notebook.ipynb", cells)
