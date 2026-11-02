"""Jev-as-a-judge: valuta trace fisse di un agent (non genera testo, decide tipizzato).

Per ogni trace chiediamo:
- grounded (Noul): la risposta è ancorata alle evidence?
- quality (Score): quanto è utile?
- search_ok (Choice): la ricerca è stata usata correttamente?
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from typesafe_sdk import Choice, Noul, Score

from jev_lab import make_client, print_decision

DATA = Path(__file__).resolve().parents[1] / "data" / "agent_traces.json"

# Soglie che puoi mettere in CI / gate di deploy.
PASS_GROUNDED = 0.70
PASS_QUALITY = 1.5  # scala 0..2 → almeno "acceptable"


QUESTIONS = {
    "grounded": Noul(
        instructions=(
            "Is the agent's final answer supported by the retrieved evidence "
            "and free of unsupported claims?"
        ),
    ),
    "quality": Score(
        instructions="How useful is the final answer for the user question?",
        criteria=[
            "Useless or wrong",
            "Acceptable but incomplete",
            "Clear, correct, and complete",
        ],
    ),
    "search_ok": Choice(
        instructions="Did the agent use search appropriately?",
        criteria={
            "appropriate": "Searched when needed, used results",
            "over_search": "Unnecessary or redundant searches",
            "under_search": "Should have searched but did not",
            "misused": "Ignored or contradicted the evidence",
        },
    ),
}


def passes(response) -> bool:
    return (
        response.nouls["grounded"].noul >= PASS_GROUNDED
        and response.scores["quality"].score >= PASS_QUALITY
        and response.choices["search_ok"].choice in {"appropriate", "over_search"}
    )


def main() -> None:
    traces = json.loads(DATA.read_text(encoding="utf-8"))
    ok = 0
    with make_client() as client:
        for trace in traces:
            state = {
                "user_question": trace["question"],
                "tools_called": trace["tools"],
                "retrieved_evidence": trace["evidence"],
                "final_answer": trace["answer"],
            }
            response = client.system_one(state=state, questions=QUESTIONS)
            print_decision(response, f"Trace: {trace['id']}")
            verdict = "PASS" if passes(response) else "FAIL"
            if verdict == "PASS":
                ok += 1
            print(f"gate: {verdict}")

    print(f"\n{ok}/{len(traces)} passano il gate (grounded≥{PASS_GROUNDED}, quality≥{PASS_QUALITY})")


if __name__ == "__main__":
    main()
