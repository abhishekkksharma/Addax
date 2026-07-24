import json
import os
import re
from pathlib import Path

from .ai_writer import write_file_ai
from .launcher import launch_app
from .llm import LLMError, ask_json, is_configured
from .search import find_file
from .workspace import open_workspace


_WORKSPACE_NAMES = set()
_config_path = Path(__file__).parent.parent / "config" / "workspaces.json"
try:
    if _config_path.exists():
        with open(_config_path, "r", encoding="utf-8") as _f:
            _WORKSPACE_NAMES = set(json.load(_f).keys())
except Exception:
    pass


def _clean(text: str) -> str:
    fillers = [
        "please", "can you", "could you", "hey", "hi", "yo",
        "buddy", "assistant", "pet", "just", "quickly", "now",
        "for me", "the", "my", "a", "an", "up", "me", "i want to",
        "i need to", "i'd like to", "go ahead and",
    ]
    result = text
    for filler in fillers:
        pattern = r"\b" + re.escape(filler) + r"\b"
        result = re.sub(pattern, " ", result)
    return " ".join(result.split()).strip()


def _contains_workspace_name(text: str) -> str | None:
    for name in _WORKSPACE_NAMES:
        if name in text:
            return name
    return None


def _create_file(filename: str) -> str:
    safe_name = os.path.basename(filename.strip()) or "untitled.txt"
    try:
        with open(safe_name, "w", encoding="utf-8") as f:
            f.write("")
        return f"Created: {safe_name}"
    except Exception as exc:
        return f"Error: {exc}"


def _llm_route(raw: str) -> str | None:
    if not is_configured():
        return None

    try:
        decision = ask_json([
            {
                "role": "system",
                "content": (
                    "Classify a Windows desktop voice command. Return JSON only with keys "
                    "intent, target, reply. intent must be one of open_app, open_workspace, "
                    "find_file, create_file, write_file, summarize_file, answer. Use answer "
                    "for unsafe, unclear, or conversational requests."
                ),
            },
            {"role": "user", "content": raw},
        ])
    except (LLMError, json.JSONDecodeError, TypeError):
        return None

    intent = str(decision.get("intent", "")).strip()
    target = str(decision.get("target", "")).strip()
    reply = str(decision.get("reply", "")).strip()

    if intent == "open_app" and target:
        return launch_app(target)
    if intent == "open_workspace" and target:
        return open_workspace(f"open {target} workspace")
    if intent == "find_file" and target:
        return find_file(target)
    if intent == "create_file" and target:
        return _create_file(target)
    if intent == "write_file":
        return write_file_ai(raw)
    if intent == "summarize_file" and target:
        from .rag import handle_rag_query
        return handle_rag_query(target, raw)
    if intent == "answer" and reply:
        return reply
    return None


def parse_and_execute(command: str) -> str:
    """
    Route voice/text commands through fast local rules first, then OpenRouter for
    ambiguous language when an API key is configured.
    """
    if not command or not command.strip():
        return "Empty command."

    raw = command.strip().lower()
    cmd = _clean(raw)

    ws_name = _contains_workspace_name(raw) or _contains_workspace_name(cmd)
    if ws_name:
        return open_workspace(f"open {ws_name} workspace")

    if "workspace" in raw:
        return open_workspace(raw)

    if any(word in cmd for word in ["open", "launch", "start", "run"]):
        match = re.search(r"(?:open|launch|start|run)\s+(.+)", cmd)
        app_name = match.group(1).strip() if match else cmd
        app_name = re.sub(r"\s+(for me|now|please)$", "", app_name).strip()
        if app_name:
            return launch_app(app_name)

    if any(word in cmd for word in ["find", "search", "look for", "locate", "where"]):
        match = re.search(r"(?:find|search|look for|locate|where(?:\s+is)?)\s+(.+)", cmd)
        filename = match.group(1).strip() if match else cmd
        if filename:
            return find_file(filename)

    if any(word in cmd for word in ["create", "make", "new file"]):
        match = re.search(r"(?:create|make|new file)\s*(?:called\s+)?([\w.\-_]+)", cmd)
        return _create_file(match.group(1) if match else "untitled.txt")

    if any(word in cmd for word in ["write", "generate", "draft", "compose"]):
        return write_file_ai(command.strip())

    if any(word in cmd for word in ["summarize", "summary", "read", "analyze"]):
        from .rag import handle_rag_query
        match = re.search(r"([\w.\-_\\/]+\.(?:pdf|csv|txt))", raw)
        if match:
            return handle_rag_query(match.group(1), raw)
        return "Specify a file, e.g. 'summarize report.pdf'"

    llm_result = _llm_route(raw)
    if llm_result:
        return llm_result

    return "I did not get that yet. Try 'open chrome', 'open dsa workspace', or 'find resume'."
