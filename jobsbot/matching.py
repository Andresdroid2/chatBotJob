import re

from .source import JobPost


def matches(job: JobPost, keyword: str) -> bool:
    """True if every word in `keyword` appears as a whole word in the title, company or tags."""
    haystack = " ".join([job.title, job.company, *job.tags]).lower()
    return all(
        re.search(rf"(?<!\w){re.escape(word)}(?!\w)", haystack) for word in keyword.lower().split()
    )