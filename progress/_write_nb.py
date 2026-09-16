"""One-off notebook writer used while refreshing labs. Not a learner artifact."""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

ROOT = Path(__file__).resolve().parents[1]

SETUP_MD = """## Setup

**Local (canonical):** this cell imports `course_setup.py` from the repo root. Your `.env` must live next to `pyproject.toml`.

**Colab:** run the two *Colab only* cells first (install + secrets), then this one. The fallback path uses `HF_TOKEN` from the environment.
"""

SETUP_COLAB_INSTALL = '''# Colab only — skip this cell locally.
# !pip install -q "smolagents[toolkit,litellm]" python-dotenv pandas requests markdownify huggingface-hub mlflow
'''

SETUP_COLAB_SECRETS = '''# Colab only — skip this cell locally.
# In Colab: Secrets (key icon) → add HF_TOKEN with "Make calls to Inference Providers".
# import os
# from google.colab import userdata
# os.environ["HF_TOKEN"] = userdata.get("HF_TOKEN")
'''

SETUP_CODE = r'''import os
import sys
from pathlib import Path

def _repo_root() -> Path | None:
    here = Path.cwd().resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "course_setup.py").exists():
            return candidate
    return None

ROOT = _repo_root()
if ROOT is not None:
    sys.path.insert(0, str(ROOT))
    from course_setup import make_model, print_setup, smoke_test

    model = make_model()
    print_setup(model)
    smoke_test(model)
else:
    from dotenv import load_dotenv
    from smolagents import InferenceClientModel

    load_dotenv()
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError(
            "course_setup.py was not found and HF_TOKEN is unset. "
            "Local: start Jupyter from the cloned repo (`uv run jupyter lab`). "
            "Colab: run the secrets cell, then re-run this cell."
        )
    model = InferenceClientModel(
        model_id=os.environ.get("COURSE_MODEL_ID", "Qwen/Qwen3-Next-80B-A3B-Thinking"),
        token=token,
    )
    print("Model initialized:", model.model_id)
'''


def write(path: Path, cells: list[tuple[str, str]]) -> None:
    nb = new_notebook(
        cells=[],
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
    )
    for kind, src in cells:
        src = src.strip("\n") + "\n"
        if kind == "md":
            nb.cells.append(new_markdown_cell(src))
        elif kind == "code":
            nb.cells.append(new_code_cell(src))
        else:
            raise ValueError(kind)
    path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, path)
    print(f"wrote {path.relative_to(ROOT)} ({len(nb.cells)} cells)")
