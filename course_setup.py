"""Shared model and environment setup for every module notebook.

Import from a notebook that lives one folder below the repo root:

    import sys
    from pathlib import Path

    ROOT = Path.cwd().resolve()
    if not (ROOT / "course_setup.py").exists():
        ROOT = ROOT.parent
    sys.path.insert(0, str(ROOT))

    from course_setup import make_model, print_setup, smoke_test

    model = make_model()
    print_setup(model)
    smoke_test(model)

Environment variables (see `.env.example`):

    COURSE_MODEL_BACKEND   hf | ollama     default: hf if HF_TOKEN else ollama
    COURSE_MODEL_ID        Hugging Face Hub id
    COURSE_HF_PROVIDER     optional provider name (together, novita, ...)
    COURSE_OLLAMA_MODEL    LiteLLM id, e.g. ollama_chat/qwen2.5-coder:7b
    OLLAMA_API_BASE        default http://localhost:11434
    HF_TOKEN               fine-grained token with Inference Providers permission
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

# Library default in smolagents 1.26 — chosen because common providers for
# Qwen2.5-Coder-32B-Instruct often lack tool calling.
DEFAULT_HF_MODEL_ID = "Qwen/Qwen3-Next-80B-A3B-Thinking"
DEFAULT_OLLAMA_MODEL = "ollama_chat/qwen2.5-coder:7b"
DEFAULT_OLLAMA_BASE = "http://localhost:11434"

# Cheaper / fallback Hub ids if the default is unavailable or too expensive.
HF_FALLBACK_MODELS = [
    "Qwen/Qwen3-Next-80B-A3B-Thinking",
    "Qwen/Qwen2.5-72B-Instruct",
    "meta-llama/Llama-3.3-70B-Instruct",
]


def _backend() -> str:
    explicit = os.environ.get("COURSE_MODEL_BACKEND", "").strip().lower()
    if explicit in {"hf", "huggingface", "inference"}:
        return "hf"
    if explicit in {"ollama", "local"}:
        return "ollama"
    if os.environ.get("HF_TOKEN"):
        return "hf"
    return "ollama"


def make_model():
    """Return a smolagents Model for the configured backend."""
    backend = _backend()
    if backend == "ollama":
        from smolagents import LiteLLMModel

        model_id = os.environ.get("COURSE_OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
        api_base = os.environ.get("OLLAMA_API_BASE", DEFAULT_OLLAMA_BASE)
        return LiteLLMModel(
            model_id=model_id,
            api_base=api_base,
            api_key=os.environ.get("OLLAMA_API_KEY", "ollama"),
            num_ctx=int(os.environ.get("COURSE_OLLAMA_NUM_CTX", "8192")),
        )

    from smolagents import InferenceClientModel

    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError(
            "HF_TOKEN is not set. Copy .env.example to .env and add a fine-grained "
            "Hugging Face token with the 'Make calls to Inference Providers' permission, "
            "or set COURSE_MODEL_BACKEND=ollama for a local model.\n"
            "Token settings: https://huggingface.co/settings/tokens"
        )
    provider = os.environ.get("COURSE_HF_PROVIDER") or None
    model_id = os.environ.get("COURSE_MODEL_ID", DEFAULT_HF_MODEL_ID)
    kwargs = {
        "model_id": model_id,
        "token": token,
    }
    if provider:
        kwargs["provider"] = provider
    return InferenceClientModel(**kwargs)


def print_setup(model) -> None:
    backend = _backend()
    model_id = getattr(model, "model_id", type(model).__name__)
    provider = getattr(model, "provider", None)
    print(f"backend : {backend}")
    print(f"class   : {type(model).__name__}")
    print(f"model   : {model_id}")
    if provider:
        print(f"provider: {provider}")
    print(f"python  : {sys.version.split()[0]}")
    try:
        import smolagents

        print(f"smolagents: {smolagents.__version__}")
    except Exception:
        pass


def smoke_test(model, prompt: str = "Reply with the single word: pong") -> str:
    """One cheap model call before any agent.run(). Raises if the backend is dead."""
    # Content must be a list of blocks: LiteLLM flattens messages as text and
    # indexes content[0]["text"]. A bare string blows up with TypeError.
    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    response = model(messages)
    text = getattr(response, "content", None) or str(response)
    if isinstance(text, list):
        # Some backends return a list of content blocks.
        parts = []
        for block in text:
            if isinstance(block, dict):
                parts.append(block.get("text", str(block)))
            else:
                parts.append(getattr(block, "text", str(block)))
        text = "".join(parts)
    text = str(text).strip()
    print("smoke test response:", text[:400])
    if not text:
        raise RuntimeError(
            "Model returned an empty response. Check HF_TOKEN permission, remaining "
            "Inference Providers credits, or that Ollama is running (`ollama serve`)."
        )
    return text
