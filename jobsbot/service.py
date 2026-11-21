from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .matching import matches
from .models import Filter, SentAlert
from .source import JobPost

MAX_FILTERS_PER_CHAT = 10
MAX_KEYWORD_LENGTH = 50
MAX_ALERTS_PER_CHAT_PER_RUN = 5 

_OLDEST = datetime.min.replace(tzinfo=UTC)


def list_filters(session: Session, chat_id: int) -> list[Filter]:
    query = select(Filter).where(Filter.chat_id == chat_id).order_by(Filter.id)
    return list(session.scalars(query))


def add_filter(session: Session, chat_id: int, keyword: str) -> str:
    """Returns 'added', 'duplicate', 'limit' or 'empty'."""
    keyword = " ".join(keyword.lower().split())[:MAX_KEYWORD_LENGTH]
    if not keyword:
        return "empty"
    existing = list_filters(session, chat_id)
    if any(f.keyword == keyword for f in existing):
        return "duplicate"
    if len(existing) >= MAX_FILTERS_PER_CHAT:
        return "limit"
    session.add(Filter(chat_id=chat_id, keyword=keyword))
    session.commit()
    return "added"


def remove_filter(session: Session, chat_id: int, position: int) -> str | None:
    """Remove the filter at 1-based `position` (as shown by /lista). Returns its keyword."""
    filters = list_filters(session, chat_id)
    if not 1 <= position <= len(filters):
        return None
    target = filters[position - 1]
    keyword = target.keyword
    session.delete(target)
    session.commit()
    return keyword


def delete_chat_data(session: Session, chat_id: int) -> None:
    """Used when a user blocks the bot."""
    session.execute(delete(Filter).where(Filter.chat_id == chat_id))
    session.execute(delete(SentAlert).where(SentAlert.chat_id == chat_id))
    session.commit()


def pending_alerts(session: Session, jobs: list[JobPost]) -> list[tuple[int, JobPost]]:
    """(chat_id, job) pairs that match a chat's filters and were not sent to it yet."""
    keywords_by_chat: dict[int, list[str]] = {}
    for f in session.scalars(select(Filter)):
        keywords_by_chat.setdefault(f.chat_id, []).append(f.keyword)

    rows = session.execute(select(SentAlert.chat_id, SentAlert.job_url))
    already_sent = {(row.chat_id, row.job_url) for row in rows}
    newest_first = sorted(jobs, key=lambda job: job.published or _OLDEST, reverse=True)

    alerts: list[tuple[int, JobPost]] = []
    for chat_id, keywords in keywords_by_chat.items():
        count = 0
        for job in newest_first:
            if (chat_id, job.url) in already_sent:
                continue
            if any(matches(job, keyword) for keyword in keywords):
                alerts.append((chat_id, job))
                count += 1
                if count >= MAX_ALERTS_PER_CHAT_PER_RUN:
                    break
    return alerts


def mark_sent(session: Session, chat_id: int, job_url: str) -> None:
    session.add(SentAlert(chat_id=chat_id, job_url=job_url))
    session.commit()