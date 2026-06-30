from datetime import datetime, timezone

import httpx
import pytest

from app.leetcode_client import LeetCodeClientError, LeetCodeGraphQLClient


def test_client_fetches_and_normalizes_recent_accepted_submissions() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://leetcode.com/graphql"
        assert request.method == "POST"
        payload = request.read().decode()
        assert "recentAcSubmissionList" in payload
        assert "kprashanth01" in payload

        return httpx.Response(
            200,
            json={
                "data": {
                    "recentAcSubmissionList": [
                        {
                            "title": "Two Sum",
                            "titleSlug": "two-sum",
                            "timestamp": "1782907200",
                            "statusDisplay": "Accepted",
                            "lang": "python3",
                        }
                    ]
                }
            },
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = LeetCodeGraphQLClient(http_client=http_client)

    submissions = client.fetch_recent_accepted_submissions(
        username="kprashanth01",
        limit=5,
    )

    assert submissions[0].title == "Two Sum"
    assert submissions[0].slug == "two-sum"
    assert submissions[0].language == "python3"
    assert submissions[0].submitted_at == datetime(
        2026, 7, 1, 12, 0, tzinfo=timezone.utc
    )
    assert submissions[0].source == "leetcode"


def test_client_raises_clear_error_when_leetcode_returns_graphql_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"errors": [{"message": "That user does not exist."}]},
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = LeetCodeGraphQLClient(http_client=http_client)

    with pytest.raises(LeetCodeClientError, match="That user does not exist"):
        client.fetch_recent_accepted_submissions(username="missing-user", limit=5)


def test_client_raises_clear_error_when_leetcode_is_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="temporarily unavailable")

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = LeetCodeGraphQLClient(http_client=http_client)

    with pytest.raises(LeetCodeClientError, match="LeetCode request failed"):
        client.fetch_recent_accepted_submissions(username="kprashanth01", limit=5)


def test_client_raises_clear_error_when_leetcode_returns_invalid_json() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not json")

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = LeetCodeGraphQLClient(http_client=http_client)

    with pytest.raises(LeetCodeClientError, match="LeetCode returned invalid JSON"):
        client.fetch_recent_accepted_submissions(username="kprashanth01", limit=5)
