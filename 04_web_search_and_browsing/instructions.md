# Module 04: Web Search & Browsing

## Learning Objectives

By the end of this module you will be able to:

1. Use `DuckDuckGoSearchTool` both as a standalone tool and inside a `CodeAgent`
2. Use `VisitWebpageTool` to fetch and read live web pages from inside an agent
3. Build a multi-step research workflow following the search → visit → extract → reason pattern
4. Apply reliability best practices to reduce hallucination and verify agent-generated citations

---

## Prerequisites

- Modules 01–03 complete (foundations, tools, CodeAgent vs ToolCallingAgent)
- `HF_TOKEN` environment variable set in your `.env` file
- Dependencies installed via `uv sync` from the project root

---

## Estimated Time

60–75 minutes

---

## How to Run

From the project root, launch the notebook with:

```bash
uv run jupyter lab 04_web_search_and_browsing/notebook.ipynb
```

Run cells from top to bottom. Do not skip the setup cell.

---

## Important Notes

### DuckDuckGo Rate Limits
DuckDuckGo actively rate-limits automated queries. If you run search cells repeatedly in quick succession you will encounter a `RatelimitException`. To avoid this:
- Wait 3–5 seconds between runs
- Do not re-run search cells unnecessarily
- If you are experimenting with the exercises, make your query changes before re-running rather than running the same query multiple times

### Websites That Block Automated Access
Some websites detect and reject automated HTTP requests. If `VisitWebpageTool` returns empty content, a CAPTCHA page, or garbled text, the site is blocking the scraper. This is normal and expected — it is not a bug. Use a different URL that contains the same information.

### max_steps for Web Research
Web research tasks can spiral: the agent searches, visits, searches again, visits again, and so on. Keep `max_steps` between 5 and 8 for most tasks. Higher values rarely improve quality and increase latency. If the agent is looping or not converging, the problem is usually an under-specified task prompt — rewrite the task before increasing `max_steps`.

---

## Common Errors and Fixes

### 1. `RatelimitException` from `duckduckgo_search`
**Cause**: too many search queries in a short time window.
**Fix**: wait 30–60 seconds and retry. Reduce how often you re-run search cells. If you are running exercises back-to-back, add `time.sleep(5)` between agent runs.

### 2. `VisitWebpageTool` returns empty content or garbage text
**Cause**: the target website is blocking automated scrapers (Cloudflare protection, JavaScript rendering requirements, or a CAPTCHA wall).
**Fix**: try a different URL that covers the same topic. For documentation, prefer official sources (e.g., `docs.huggingface.co`, `python.org`) which are generally more scraper-friendly than third-party blogs.

### 3. Agent loops searching the same query repeatedly
**Cause**: the task is too vague, so the agent cannot determine when it has enough information to stop.
**Fix**: make the task more specific. Instead of "Tell me about Python releases", use "Visit python.org/downloads and extract the exact version number of the latest stable Python release." If the task is already specific, increase `max_steps` by 2–3.

### 4. Agent returns URLs it did not actually find via search
**Cause**: the agent is hallucinating URLs — generating plausible-looking links from its training data rather than from actual search results.
**Fix**: add an explicit instruction to the task prompt: "Only use URLs that you found via the search tool. Do not generate URLs from memory." Also ask the agent to return the source URL alongside every factual claim so you can verify it.
