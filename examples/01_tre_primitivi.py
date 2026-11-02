"""I tre primitivi di Jev: Noul, Choice, Score — una sola chiamata, tre risposte tipizzate.

Jev NON genera testo. Legge lo `state`, valuta le `questions` e restituisce
distribuzioni di probabilità (calibrate su hosted Jev).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from typesafe_sdk import Choice, Noul, Score

from jev_lab import make_client, print_decision

STATE = {
    "ticket": (
        "I was charged twice for the same invoice. "
        "Please refund the duplicate charge today — we cannot close the books."
    )
}

QUESTIONS = {
    # Noul = "è vero?" → probabilità 0..1
    "is_billing": Noul(instructions="Is this ticket about billing or payments?"),
    # Choice = scegli UNA etichetta tra opzioni fisse
    "tone": Choice(
        instructions="What is the customer's tone?",
        criteria={
            "calm": "Matter-of-fact, no strong emotion",
            "frustrated": "Annoyed but civil",
            "angry": "Hostile or aggressive language",
        },
    ),
    # Score = scala ORDINALE (l'ordine conta)
    "urgency": Score(
        instructions="How urgent is a reply?",
        criteria=["can wait", "this week", "today / ASAP"],
    ),
}


def main() -> None:
    with make_client() as client:
        response = client.system_one(state=STATE, questions=QUESTIONS)

    print_decision(response, "Tre primitivi sullo stesso ticket")

    # Tipico uso a valle: soglie sulle probabilità, non parsing di testo.
    p_billing = response.nouls["is_billing"].noul
    if p_billing >= 0.8:
        print(f"\n-> Azione: route a Billing (p={p_billing:.2f})")
    else:
        print(f"\n-> Azione: non e' billing chiaro (p={p_billing:.2f})")


if __name__ == "__main__":
    main()
