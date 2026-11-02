"""Stampa leggibile delle risposte System One."""

from __future__ import annotations

from typing import Any


def print_decision(response: Any, title: str = "Decisione") -> None:
    print(f"\n=== {title} ===")
    if getattr(response, "model", None):
        print(f"model: {response.model}")

    for name, ans in getattr(response, "nouls", {}).items():
        print(f"[noul]  {name}: P(yes)={ans.noul:.3f}")

    for name, ans in getattr(response, "choices", {}).items():
        probs = ""
        if getattr(ans, "probabilities", None):
            top = sorted(ans.probabilities.items(), key=lambda x: -x[1])[:3]
            probs = "  probs=" + ", ".join(f"{k}:{v:.2f}" for k, v in top)
        conf = f"  conf={ans.confidence:.2f}" if getattr(ans, "confidence", None) is not None else ""
        print(f"[choice] {name}: {ans.choice}{conf}{probs}")

    for name, ans in getattr(response, "scores", {}).items():
        legend = ""
        if getattr(ans, "legend", None):
            legend = "  legend=" + str(ans.legend)
        conf = f"  conf={ans.confidence:.2f}" if getattr(ans, "confidence", None) is not None else ""
        print(f"[score]  {name}: {ans.score:.2f}{conf}{legend}")
