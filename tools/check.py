"""Validate starter configuration, scripts, documentation links, and skill mirrors."""
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

from common import ROOT, config


def check(root=ROOT):
    config(root)
    paths = []
    for directory in ("tools", "tests/base", "docs", ".agents", ".claude", ".codex"):
        paths.extend((root / directory).rglob("*"))
    paths.extend(root.glob("*.md"))
    for path in paths:
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.suffix == ".py":
            ast.parse(path.read_text(), filename=str(path))
        elif path.suffix == ".sh":
            subprocess.run(["bash", "-n", str(path)], check=True)
        elif path.suffix == ".json" and not path.name.endswith(".local.json"):
            json.loads(path.read_text())
        elif path.suffix == ".toml" and sys.version_info >= (3, 11):
            import tomllib
            tomllib.loads(path.read_text())
        elif path.suffix == ".md":
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" in target or target.startswith("#"):
                    continue
                target = target.split("#")[0]
                if not (path.parent / target).exists():
                    raise ValueError(f"{path.relative_to(root)}: broken link {target}")
    if (root / "CLAUDE.md").read_text().strip() != "@AGENTS.md":
        raise ValueError("CLAUDE.md should import the shared AGENTS.md")
    source = root / ".agents" / "skills"
    mirror = root / ".claude" / "skills"
    for path in source.rglob("SKILL.md"):
        text = path.read_text()
        if not text.startswith("---\n") or "\ndescription:" not in text.split("---", 2)[1]:
            raise ValueError(f"{path}: missing skill frontmatter")
        other = mirror / path.relative_to(source)
        if not other.is_file() or other.read_text() != text:
            raise ValueError(f"skill mirror differs: {other}; run python3 tools/sync_skills.py")
    if {str(p.relative_to(mirror)) for p in mirror.rglob("SKILL.md")} != {str(p.relative_to(source)) for p in source.rglob("SKILL.md")}:
        raise ValueError("Claude skill inventory differs from .agents/skills")
    print("[check] configuration, Python/shell syntax, documentation links, and skill mirrors pass")


if __name__ == "__main__":
    try:
        check()
    except (ValueError, OSError, SyntaxError, subprocess.CalledProcessError) as exc:
        sys.exit(f"[check] {exc}")
