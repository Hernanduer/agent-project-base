"""Keep delegation ownership in the main session; no provider log paths."""
import json
import sys


def reason(event):
    transcript = str(event.get("transcript_path") or "").replace("\\", "/")
    child = bool(event.get("agent_id")) or "/subagents/" in transcript
    if child and event.get("tool_name") in ("Agent", "Task", "Workflow"):
        return ("Only the main session delegates work. Complete your assigned scope or "
                "return a handoff with remaining steps; do not launch nested agents.")
    return None


if __name__ == "__main__":
    try:
        message = reason(json.load(sys.stdin))
        if message:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                "permissionDecision": "deny", "permissionDecisionReason": message}}))
    except (ValueError, TypeError, AttributeError):
        pass
