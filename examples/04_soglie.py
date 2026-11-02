"""Perché le probabilità importano: stessa decisione, politiche diverse.

Senza calibrazione (modelli open locali) le soglie vanno validate sui tuoi label.
Con hosted Jev puoi usare soglie più stabili in produzione.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from typesafe_sdk import Noul

from jev_lab import make_client

MESSAGES = [
    "Can you remind me what plan I'm on?",
    "We are losing $12k/hour — checkout is 500ing for all EU traffic.",
    "Thanks, the refund arrived. Closing this.",
]


def policy(p: float) -> str:
    if p >= 0.90:
        return "auto-page on-call"
    if p >= 0.60:
        return "create P1 ticket"
    if p >= 0.30:
        return "queue for human review"
    return "ignore / low priority"


def main() -> None:
    with make_client() as client:
        for msg in MESSAGES:
            r = client.system_one(
                state=msg,
                questions={
                    "sev": Noul(
                        instructions=(
                            "Does this message describe an active production incident "
                            "or revenue-impacting outage?"
                        )
                    )
                },
            )
            p = r.nouls["sev"].noul
            print(f"\nmsg: {msg}")
            print(f"P(incident)={p:.3f}  ->  {policy(p)}")


if __name__ == "__main__":
    main()
