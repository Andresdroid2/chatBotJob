import pytest

from jobsbot.db import init_db
from jobsbot.matching import matches
from jobsbot.service import (
    add_filter,
    list_filters,
    mark_sent,
    pending_alerts,
    remove_filter,
)
from jobsbot.source import JobPost

CHAT = 111


@pytest.fixture
def session():
    factory = init_db("sqlite://")
    with factory() as s:
        yield s


def make_job(n: int, title="Junior Python Developer") -> JobPost:
    return JobPost(title=title, company="Acme", url=f"https://example.com/{n}", source="Test")


def test_matches_whole_words_only():
    job = make_job(1, title="JavaScript Developer")
    assert not matches(job, "java")
    assert matches(job, "javascript")


def test_add_filter_normalizes_and_rejects_duplicates(session):
    assert add_filter(session, CHAT, "  Python   JUNIOR ") == "added"
    assert add_filter(session, CHAT, "python junior") == "duplicate"
    assert [f.keyword for f in list_filters(session, CHAT)] == ["python junior"]


def test_remove_filter_by_position(session):
    add_filter(session, CHAT, "python")
    add_filter(session, CHAT, "django")
    assert remove_filter(session, CHAT, 1) == "python"
    assert remove_filter(session, CHAT, 5) is None


def test_pending_alerts_match_and_do_not_repeat(session):
    add_filter(session, CHAT, "python junior")
    jobs = [make_job(1), make_job(2, title="Senior Java Developer")]
    alerts = pending_alerts(session, jobs)
    assert [(chat, job.url) for chat, job in alerts] == [(CHAT, "https://example.com/1")]
    mark_sent(session, CHAT, "https://example.com/1")
    assert pending_alerts(session, jobs) == []