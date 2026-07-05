import os
import re
import time

from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash"


class QuotaExhaustedError(RuntimeError):
    pass


def make_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Get a free key at https://ai.google.dev "
            "and put it in .env (see .env.example) or in the environment."
        )
    return genai.Client(api_key=api_key)


def _is_rate_limit(err: Exception) -> bool:
    return "429" in str(err) or "RESOURCE_EXHAUSTED" in str(err)


def _is_daily_quota(err: Exception) -> bool:
    return "PerDay" in str(err) or "RequestsPerDay" in str(err)


def _retry_after(err: Exception) -> float | None:
    m = re.search(r"retryDelay['\"]?\s*[:=]\s*['\"]?(\d+(?:\.\d+)?)s", str(err))
    return float(m.group(1)) if m else None


def generate_structured(client, prompt, system, schema, retries: int = 2):
    config = types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json",
        response_schema=schema,
        temperature=0,
    )
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            resp = client.models.generate_content(model=MODEL, contents=prompt, config=config)
            if isinstance(resp.parsed, schema):
                return resp.parsed
            return schema.model_validate_json(resp.text or "")
        except Exception as err:
            last = err
            if _is_rate_limit(err) and _is_daily_quota(err):
                raise QuotaExhaustedError(
                    "Gemini daily free-tier quota exhausted (requests-per-day). It resets "
                    "around midnight Pacific — try again later or use a higher tier / another key."
                ) from err
            if attempt >= retries:
                break
            time.sleep((_retry_after(err) or 1.5 * (attempt + 1)) + 0.5)
    raise RuntimeError(f"generation failed after {retries + 1} attempts: {last}")
