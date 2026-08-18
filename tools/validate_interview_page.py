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
        (html.count('class="pressure-answer"') == len(pressure_questions), "pressure answer block count mismatch"),
        ("严厉面试官追问题库" in html, "missing strict interviewer section title"),
        ("data-pressure-cat" in html, "pressure questions must expose searchable category metadata"),
        ("完整口语化回答" in html, "missing pressure answer label"),
        ("答题要点" in html, "missing pressure answer points label"),
        ("避坑提醒" in html, "missing pressure avoid label"),
    ]

    for ok, message in checks:
        if not ok:
            fail(message)

    required_question_fields = {"cat", "q", "a", "k", "follow", "avoid"}
    for index, item in enumerate(questions, 1):
        missing = [key for key in required_question_fields if not str(item.get(key, "")).strip()]
        if missing:
            fail(f"detailed question {index} missing fields: {', '.join(missing)}")

    required_pressure_fields = {"cat", "q", "risk", "focus", "answer", "points", "avoid"}
    for index, item in enumerate(pressure_questions, 1):
        missing = [key for key in required_pressure_fields if not str(item.get(key, "")).strip()]
        if missing:
            fail(f"pressure question {index} missing fields: {', '.join(missing)}")
        if len(str(item["answer"])) < 45:
            fail(f"pressure question {index} answer is too short")
        if len(str(item["answer"])) < 90:
            fail(f"pressure question {index} answer is not complete enough")
        weak_answer_markers = [
            "然后把话题收回",
            "这题先别急着背概念",
            "这题要",
            "然后强调",
            "然后按链路讲",
        ]
        if any(marker in str(item["answer"]) for marker in weak_answer_markers):
            fail(f"pressure question {index} still uses a generic answer template")
        if not isinstance(item["points"], (list, tuple)) or len(item["points"]) < 2:
            fail(f"pressure question {index} must have at least two answer points")
        if len(str(item["avoid"])) < 15:
            fail(f"pressure question {index} avoid text is too short")

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
