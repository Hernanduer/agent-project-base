"""Copy canonical repo skills to Claude's discovery directory; no symlinks."""
import shutil

from common import ROOT

source = ROOT / ".agents" / "skills"
mirror = ROOT / ".claude" / "skills"
for skill in sorted(source.glob("*/SKILL.md")):
    target = mirror / skill.relative_to(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(skill, target)
    print(target.relative_to(ROOT))
