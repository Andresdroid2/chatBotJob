import httpx
import respx

from jobsbot.source import REMOTEOK_URL, REMOTIVE_URL, fetch_all_jobs, fetch_remotive

REMOTIVE_PAYLOAD = {
    "jobs": [
        {
            "title": "Junior Python Developer",
            "company_name": "Acme",
            "url": "https://remotive.com/job/1",
            "tags": ["python"],
            "publication_date": "2026-11-10T10:00:00",
        },
        {"title": "Job without url"},
    ]
}

REMOTEOK_PAYLOAD = [
    {"legal": "terms of use"},
    {"position": "Backend Engineer", "company": "Globex", "url": "https://remoteok.com/r/2"},
]


@respx.mock
async def test_fetch_remotive_skips_invalid_items():
    respx.get(REMOTIVE_URL).mock(return_value=httpx.Response(200, json=REMOTIVE_PAYLOAD))
    async with httpx.AsyncClient() as client:
        jobs = await fetch_remotive(client)
    assert [job.title for job in jobs] == ["Junior Python Developer"]


@respx.mock
async def test_fetch_all_survives_one_failing_source():
    respx.get(REMOTIVE_URL).mock(return_value=httpx.Response(500))
    respx.get(REMOTEOK_URL).mock(return_value=httpx.Response(200, json=REMOTEOK_PAYLOAD))
    async with httpx.AsyncClient() as client:
        jobs = await fetch_all_jobs(client)
    assert [job.source for job in jobs] == ["RemoteOK"]