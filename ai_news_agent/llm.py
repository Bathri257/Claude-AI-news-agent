"""Thin wrapper around the Claude API: one JSON-schema-constrained request."""
from __future__ import annotations

import json
import os

import anthropic

FALLBACK_BETA = "server-side-fallback-2026-07-01"


def available() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN"))


_client: anthropic.Anthropic | None = None


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(max_retries=4)
    return _client


def ask_json(model: str, system: str, prompt: str, schema: dict, effort: str) -> dict:
    """Send one request and return the parsed JSON object the schema describes."""
    with client().beta.messages.stream(
        model=model,
        max_tokens=32000,
        system=system,
        messages=[{"role": "user", "content": prompt}],
        output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
        betas=[FALLBACK_BETA],
        fallbacks="default",  # if a safety classifier declines, retry on a fallback model
    ) as stream:
        response = stream.get_final_message()
    if response.stop_reason == "refusal":
        raise RuntimeError(f"Request declined: {response.stop_details}")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Response hit max_tokens")
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)
