import os

import httpx


class EmailConfigurationError(Exception):
    pass


class EmailDeliveryError(Exception):
    pass


class ResendEmailSender:
    def __init__(
        self,
        api_key: str | None = None,
        from_email: str | None = None,
    ) -> None:
        self._api_key = api_key or os.getenv("RESEND_API_KEY")
        self._from_email = from_email or os.getenv("EMAIL_FROM")

    def send_email(self, to_email: str, subject: str, html: str) -> str:
        if not self._api_key or not self._from_email:
            raise EmailConfigurationError(
                "RESEND_API_KEY and EMAIL_FROM must be configured."
            )

        try:
            response = httpx.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": self._from_email,
                    "to": [to_email],
                    "subject": subject,
                    "html": html,
                },
                timeout=10,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise EmailDeliveryError("Resend could not send the email.") from exc

        body = response.json()
        email_id = body.get("id")
        if not isinstance(email_id, str):
            raise EmailDeliveryError("Resend returned an invalid response.")
        return email_id
