from typing import Literal

from pydantic import BaseModel, Field

import llm

BATCH_SIZE = 20

SYSTEM = """\
You are a product-review sentiment classifier. You receive a numbered list of
reviews. For EACH review return its number, a sentiment of exactly 'positive',
'negative', or 'neutral', and a confidence 0-1. 'neutral' is for mixed or
factual reviews with no clear lean. Return one result per review, in order."""


class ReviewSentiment(BaseModel):
    index: int = Field(description="1-based number of the review within the batch")
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float = Field(ge=0, le=1)


class SentimentBatch(BaseModel):
    results: list[ReviewSentiment]


def analyze(client, texts: list[str]) -> list[str]:
    labels: list[str] = ["neutral"] * len(texts)
    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start : start + BATCH_SIZE]
        numbered = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(batch))
        result = llm.generate_structured(
            client, f"Reviews:\n{numbered}", SYSTEM, SentimentBatch
        )
        for r in result.results:
            pos = start + (r.index - 1)
            if start <= pos < start + len(batch):
                labels[pos] = r.sentiment
    return labels
