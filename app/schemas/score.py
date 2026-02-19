from enum import Enum

class Score(str, Enum):
    """Enumeration for evaluation scores."""

    no_relevance = "0"
    low_relevance = "1"
    medium_relevance = "2"
    high_relevance = "3"

# Score description (reused across all metrics)
SCORE_DESCRIPTION = (
    "Score as a string between '0' and '3'. "
    "0: No relevance/Not grounded/Poor quality - Completely fails the criterion. "
    "1: Low relevance/Low groundedness/Below average - Minimal adherence to criterion. "
    "2: Medium relevance/Medium groundedness/Good - Mostly meets the criterion. "
    "3: High relevance/High groundedness/Excellent - Fully meets the criterion."
)