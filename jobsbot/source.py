import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx

logger = logging.getLogger(__name__)

REMOTIVE_URL = "https://remotive.com/api/remote-jobs"
REMOTEOK_URL = "https://remoteok.com/api"


@dataclass(frozen=True)
class JobPost:
    title: str
    company: str
    url: str
    source: str
    tags: tuple[str, ...] = ()
    location: str = ""
    published: datetime | None = None


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _parse_remotive(item: dict) -> JobPost | None:
    title, url = item.get("title"), item.get("url")
    if not title or not url:
        return None
    return JobPost(
        title=title,
        company=item.get("company_name") or "",
        url=url,
        source="Remotive",
        tags=tuple(item.get("tags") or ()),
        location=item.get("candidate_required_location") or "",
        published=_parse_date(item.get("publication_date")),
    )


def _parse_remoteok(item: dict) -> JobPost | None:
    title, url = item.get("position"), item.get("url")
    if not title or not url:
        return None
    return JobPost(
        title=title,
        company=item.get("company") or "",
        url=url,
        source="RemoteOK",
        tags=tuple(item.get("tags") or ()),
        location=item.get("location") or "",
        published=_parse_date(item.get("date")),
    )


async def fetch_remotive(client: httpx.AsyncClient) -> list[JobPost]:
    response = await client.get(REMOTIVE_URL)
    response.raise_for_status()
    posts = (_parse_remotive(item) for item in response.json().get("jobs", []))
    return [post for post in posts if post]


async def fetch_remoteok(client: httpx.AsyncClient) -> list[JobPost]:
    response = await client.get(REMOTEOK_URL)
    response.raise_for_status()
    posts = (_parse_remoteok(item) for item in response.json()[1:])
    return [post for post in posts if post]


Fetcher = Callable[[httpx.AsyncClient], Awaitable[list[JobPost]]]
SOURCES: tuple[Fetcher, ...] = (fetch_remotive, fetch_remoteok)


async def fetch_all_jobs(client: httpx.AsyncClient) -> list[JobPost]:
    results = await asyncio.gather(*(fetch(client) for fetch in SOURCES), return_exceptions=True)
    jobs: dict[str, JobPost] = {}
    for fetch, result in zip(SOURCES, results, strict=True):
        if isinstance(result, BaseException):
            logger.warning("Source %s failed: %r", fetch.__name__, result)
            continue
        for job in result:
            jobs.setdefault(job.url, job)
    return list(jobs.values())