from __future__ import annotations

import re
import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
BUILDER = ROOT / "tools" / "build_interview_page.py"


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    ns = runpy.run_path(str(BUILDER))

    questions = ns.get("questions", [])
    tech_points = ns.get("tech_points", [])
    pressure_questions = ns.get("pressure_questions", [])

    checks = [
        (html.lstrip().startswith("<!doctype html>"), "index.html must start with <!doctype html>"),
        (html.rstrip().endswith("</html>"), "index.html must close with </html>"),
        (len(questions) == 54, "expected 54 detailed interview question cards"),
        (len(tech_points) == 20, "expected 20 technical knowledge cards"),
        (len(pressure_questions) == 130, "expected 130 strict follow-up questions"),
        (html.count('class="qa-card') == len(questions), "detailed question card count mismatch"),
        (html.count('class="tech-card') == len(tech_points), "technical card count mismatch"),
        (html.count('class="pressure-item') == len(pressure_questions), "pressure question count mismatch"),
        ("严厉面试官追问题库" in html, "missing strict interviewer section title"),
        ("data-pressure-cat" in html, "pressure questions must expose searchable category metadata"),
    ]

    for ok, message in checks:
        if not ok:
            fail(message)

    required_question_fields = {"cat", "q", "a", "k", "follow", "avoid"}
    for index, item in enumerate(questions, 1):
        missing = [key for key in required_question_fields if not str(item.get(key, "")).strip()]
        if missing:
            fail(f"detailed question {index} missing fields: {', '.join(missing)}")

    required_pressure_fields = {"cat", "q", "risk", "focus"}
    for index, item in enumerate(pressure_questions, 1):
        missing = [key for key in required_pressure_fields if not str(item.get(key, "")).strip()]
        if missing:
            fail(f"pressure question {index} missing fields: {', '.join(missing)}")

    if re.search(r"TODO|TBD|X%|\[填写", html):
        fail("placeholder text found")

    print(
        "ok: "
        f"{len(questions)} detailed questions, "
        f"{len(pressure_questions)} pressure questions, "
        f"{len(tech_points)} tech cards"
    )


if __name__ == "__main__":
    main()
