import httpx
import pytest

from app.auth import SupabaseAuthClient, SupabaseAuthError


def test_supabase_auth_client_returns_current_user_for_valid_token() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://project.supabase.co/auth/v1/user"
        assert request.headers["authorization"] == "Bearer valid-token"
        assert request.headers["apikey"] == "publishable-key"
        return httpx.Response(
            200,
            json={"id": "user-1", "email": "user@example.com"},
        )

    client = SupabaseAuthClient(
        supabase_url="https://project.supabase.co",
        publishable_key="publishable-key",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    user = client.get_user("valid-token")

    assert user.id == "user-1"
    assert user.email == "user@example.com"


def test_supabase_auth_client_rejects_invalid_token() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"message": "invalid token"})

    client = SupabaseAuthClient(
        supabase_url="https://project.supabase.co",
        publishable_key="publishable-key",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(SupabaseAuthError):
        client.get_user("bad-token")
