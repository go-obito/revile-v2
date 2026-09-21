from __future__ import annotations

import httpx

from app.config import Settings


class NewsletterDeliveryError(RuntimeError):
    pass


class ResendNewsletter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _ensure_configured(self) -> None:
        if not all((self.settings.resend_api_key, self.settings.resend_audience_id, self.settings.newsletter_from_email)):
            raise NewsletterDeliveryError("Newsletter delivery is not configured.")

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.settings.resend_api_key}", "Content-Type": "application/json"}

    async def send_confirmation(self, email: str, confirmation_url: str) -> None:
        self._ensure_configured()
        payload = {
            "from": self.settings.newsletter_from_email,
            "to": [email],
            "subject": "Confirm your Revile briefing subscription",
            "html": (
                "<p>Confirm your subscription to the Revile briefing.</p>"
                f'<p><a href="{confirmation_url}">Confirm subscription</a></p>'
                "<p>If you did not request this, you can ignore this message.</p>"
            ),
        }
        await self._request("POST", "/emails", payload)

    async def subscribe_contact(self, email: str) -> str | None:
        self._ensure_configured()
        response = await self._request(
            "POST",
            f"/audiences/{self.settings.resend_audience_id}/contacts",
            {"email": email, "unsubscribed": False},
        )
        return response.get("id") if isinstance(response, dict) else None

    async def set_contact_subscription(self, contact_id: str, subscribed: bool) -> None:
        self._ensure_configured()
        await self._request(
            "PATCH",
            f"/audiences/{self.settings.resend_audience_id}/contacts/{contact_id}",
            {"unsubscribed": not subscribed},
        )

    async def unsubscribe_contact(self, contact_id: str) -> None:
        await self.set_contact_subscription(contact_id, subscribed=False)

    async def _request(self, method: str, path: str, payload: dict[str, object]) -> dict[str, object]:
        try:
            async with httpx.AsyncClient(base_url="https://api.resend.com", timeout=10) as client:
                response = await client.request(method, path, headers=self._headers(), json=payload)
            if response.is_error:
                raise NewsletterDeliveryError("The newsletter provider could not process the request.")
            data = response.json()
            return data if isinstance(data, dict) else {}
        except (httpx.HTTPError, ValueError) as exc:
            raise NewsletterDeliveryError("The newsletter provider is unavailable.") from exc
