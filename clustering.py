from pydantic import BaseModel, Field

import llm

SYSTEM = """\
You are a product analyst. You receive all reviews for one product. Identify the
RECURRING themes, separated into complaints and praises. Merge synonyms into one
theme (e.g. "battery dies fast" and "poor battery life" are one theme). For each
theme give: a short theme label, the number of reviews that mention it (an honest
count based on the reviews shown), and one short verbatim example quote from the
reviews. Return the top themes by mention count, most-mentioned first."""


class Theme(BaseModel):
    theme: str = Field(description="short theme label, e.g. 'Battery life'")
    mention_count: int = Field(ge=0, description="how many reviews mention it")
    example_quote: str = Field(description="a short verbatim quote from a review")


class ThemeReport(BaseModel):
    top_complaints: list[Theme] = Field(default_factory=list)
    top_praises: list[Theme] = Field(default_factory=list)


def extract_themes(client, texts: list[str]) -> ThemeReport:
    joined = "\n".join(f"- {t}" for t in texts)
    return llm.generate_structured(
        client, f"All reviews ({len(texts)}):\n{joined}", SYSTEM, ThemeReport
    )
