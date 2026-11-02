"""Caso d'uso concreto: instradare ticket di supporto con Choice + Noul + Score.

Idea: una sola decisione → team, urgenza, escalate-to-human.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from typesafe_sdk import Choice, Noul, Score

from jev_lab import make_client, print_decision

DATA = Path(__file__).resolve().parents[1] / "data" / "tickets.json"

QUESTIONS = {
    "team": Choice(
        instructions="Which team should own this ticket?",
        criteria={
            "billing": "Payments, invoices, refunds, subscriptions",
            "technical": "Bugs, outages, API/integration failures",
            "sales": "Pricing, upgrades, account questions",
            "other": "Does not fit the teams above",
        },
    ),
    "urgency": Score(
        instructions="How soon must someone reply?",
        criteria=[
            "Can wait days",
            "Should reply this week",
            "Needs same-day attention",
            "Active outage / revenue blocked",
        ],
    ),
    "escalate": Noul(
        instructions="Should a human agent handle this instead of an automated reply?",
    ),
}


def decide_action(response) -> str:
    team = response.choices["team"].choice
    urgency = response.scores["urgency"].score  # expected level 0..3
    escalate_p = response.nouls["escalate"].noul

    if escalate_p >= 0.75 or urgency >= 2.5:
        return f"ESCALATE -> human ({team}), urgency={urgency:.1f}, p_esc={escalate_p:.2f}"
    if urgency >= 1.5:
        return f"QUEUE priority -> {team}"
    return f"AUTO-ACK -> {team}"


def main() -> None:
    tickets = json.loads(DATA.read_text(encoding="utf-8"))
    with make_client() as client:
        for i, ticket in enumerate(tickets, 1):
            response = client.system_one(
                state={"subject": ticket["subject"], "body": ticket["body"]},
                questions=QUESTIONS,
            )
            print_decision(response, f"Ticket {i}: {ticket['subject']}")
            print(f"azione: {decide_action(response)}")


if __name__ == "__main__":
    main()
