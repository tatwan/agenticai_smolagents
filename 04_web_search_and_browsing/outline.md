# Module 04: Web Search & Browsing

**Read this first**, then run `notebook.ipynb`.

**Time:** 75–90 minutes · **Depends on:** Modules 01–03 · **Flaky by nature:** free search and bot-blocking sites

---

## 1. What problem does retrieval solve?

Language models have **closed** information: whatever was in the training mix, frozen at some cutoff. They are excellent at *transforming* text they can see. They are unreliable at *facts that move*.

**Open** information lives outside the weights: today’s Python release, a pricing page, a changelog, a news item.

An agent with web tools is not “smarter.” It is **allowed to look**. That is the same move as RAG (retrieve chunks from *your* corpus) or an SQL tool (retrieve rows from *your* warehouse). Different stores, same idea: **do not ask the weights for data they were never given.**

| Store | Tool-shaped access | Failure mode |
|---|---|---|
| Public web | Search + visit | Rate limits, bot walls, junk snippets |
| Your docs | Retriever / MCP | Wrong chunk, stale index |
| Your database | SQL tool | Bad query, missing join |
| Model weights | (none — just generate) | Confident fiction |

---

## 2. When to search vs when to stay closed

Search when **recency, attribution, or a specific URL** matters.

Stay closed (or use a local file tool) when:

- The task is transformation (“rewrite this,” “compute that”)
- You already have the document
- You cannot tolerate non-determinism or third-party HTML

Search is slow, rate-limited, and politically messy (ToS, scraping). Use it as a last source of *facts*, not as a personality.

---

## 3. How a research hop should go

Humans do this. Good agents should too:

1. **Search** — get titles, URLs, snippets
2. **Select** — pick one or two sources (official docs beat random blogs)
3. **Visit** — fetch the page as text
4. **Extract** — pull the field you actually needed
5. **Cite** — return the URL you used, not one you invented

Skipping “visit” is how you get snippet-extrapolation: the model fills gaps with plausible lies. Skipping “cite” is how you cannot check.

**Ask for the source URL in the task.** That single instruction catches a lot of citation hallucination.

`max_steps` of 5–8 is enough for one fact. If the agent loops, the prompt is vague; do not just raise the fuse.

---

## 4. How smolagents implements this (1.26)

**Teach `WebSearchTool`.** It is what current docs lead with.

```python
from smolagents import WebSearchTool, VisitWebpageTool

search = WebSearchTool(max_results=5, engine="duckduckgo")  # also "bing", "exa"
print(search("smolagents huggingface 2026"))

visit = VisitWebpageTool(max_output_length=40000)
print(visit("https://huggingface.co/docs/smolagents")[:500])
```

| Tool | Engine / notes |
|---|---|
| `WebSearchTool` | `engine="duckduckgo"` (HTML lite), `"bing"` (RSS), `"exa"` (needs `EXA_API_KEY`) |
| `DuckDuckGoSearchTool` | Still shipped; uses the `ddgs` package. Same `name` (`web_search`). Prefer `WebSearchTool` in new code. |
| `VisitWebpageTool` | GET + HTML→markdown, truncated. JS-heavy and Cloudflare pages will look empty or like a CAPTCHA. That is not your bug. |

`add_base_tools=True` on `CodeAgent` injects DuckDuckGo search **and** visit-webpage. In this module we pass the tools **explicitly** so you can see them.

Rate limits: wait a few seconds between searches. Broad queries (`"AI"`) die faster than specific ones (`"Python 3.13 official download page"`).

`engine="duckduckgo"` scrapes DuckDuckGo Lite and **often returns zero hits** from datacenter IPs or after a layout change. The notebook falls back to `engine="bing"`. That is expected, not a failed install.

---

## 5. Reliability guards (any web agent)

- **Specific task** beats “tell me about X.”
- **Official domain** in the prompt (`python.org`, `docs.huggingface.co`).
- **Cite the URL.** Then click it yourself for anything that matters.
- **Expect blocks.** Have a fallback URL or a smaller question.
- **Do not trust a URL the model wrote** unless it appeared in a tool observation.

---

## 6. Exercises

1. **Python version (default)** — search + visit `python.org`; extract the latest stable version; print steps; say whether it visited or only searched.
2. **Stretch** — three recent articles on a topic you care about, comparison table with URLs, `max_steps=10`. If rate-limited, stop at one article and write what you would change. (dbt is a fine topic; so is smolagents itself.)

---

## 7. What you should be able to say out loud

- Retrieval is how agents get open information. The web is one store among many.
- Search snippets are not the page. Visit before you quote.
- Citations the model invents are not citations.
- Free search will flake. That is part of the lab.

**Next — Module 05.** One agent with search + math + writing becomes a mess. A manager with named specialists — *descriptions as a routing table* — is the next pattern.
