import os
from typing import Annotated

import httpx
from fastapi import Header, HTTPException, status
from pydantic import BaseModel


class CurrentUser(BaseModel):
    id: str
    email: str | None = None


class SupabaseAuthError(Exception):
    pass


class SupabaseAuthClient:
    def __init__(
        self,
        supabase_url: str | None = None,
        publishable_key: str | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._supabase_url = (supabase_url or os.getenv("SUPABASE_URL") or "").rstrip(
            "/"
        )
        self._publishable_key = publishable_key or os.getenv(
            "SUPABASE_PUBLISHABLE_KEY",
            "",
        )
        self._http_client = http_client or httpx.Client(timeout=10.0)

    def get_user(self, access_token: str) -> CurrentUser:
        if not self._supabase_url or not self._publishable_key:
            raise SupabaseAuthError("Supabase auth is not configured")

        try:
            response = self._http_client.get(
                f"{self._supabase_url}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "apikey": self._publishable_key,
                },
            )
        except httpx.HTTPError as exc:
            raise SupabaseAuthError("Could not reach Supabase Auth") from exc

        if response.status_code != status.HTTP_200_OK:
            raise SupabaseAuthError("Invalid Supabase access token")

        body = response.json()
        return CurrentUser(id=body["id"], email=body.get("email"))


def get_auth_client() -> SupabaseAuthClient:
    return SupabaseAuthClient()


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> CurrentUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    try:
        return get_auth_client().get_user(token)
    except SupabaseAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session.",
        ) from exc
