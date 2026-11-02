"""Client TypeSafe configurato da .env (hosted Jev o server locale /v1/systemone)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient

# Carica .env dalla root del repo se presente.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def make_client() -> TypeSafeClient:
    """Crea un TypeSafeClient.

    Legge:
    - TYPESAFE_API_KEY (obbligatoria; per locale puoi usare "local")
    - TYPESAFE_BASE_URL (opzionale; default = API TypeSafe)
    - TYPESAFE_DEFAULT_MODEL (opzionale; default = jev-latest)
    """
    api_key = os.getenv("TYPESAFE_API_KEY")
    if not api_key:
        raise SystemExit(
            "Manca TYPESAFE_API_KEY.\n"
            "Copia .env.example in .env e scegli:\n"
            "  A) key TypeSafe (hosted Jev)\n"
            "  B) server locale: TYPESAFE_BASE_URL=http://127.0.0.1:8795 e KEY=local\n"
            "  C) Codiv/OpenJev: vedi .env.example"
        )

    kwargs: dict = {"api_key": api_key}
    base_url = os.getenv("TYPESAFE_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url
    model = os.getenv("TYPESAFE_DEFAULT_MODEL")
    if model:
        kwargs["model"] = model
    return TypeSafeClient(**kwargs)
