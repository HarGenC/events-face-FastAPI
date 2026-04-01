import time
from uuid import UUID

import httpx
from loguru import logger

from app.core.config import settings
from app.modules.clients.async_retry import AsyncRetry
from app.modules.tickets.schemas import RegistrationInfoIn
from app.observability.metrics import (
    events_provider_request_duration_seconds,
    events_provider_requests_total,
)


class EventsProviderClient:
    events: list | None

    def __init__(self, async_retry: AsyncRetry | None = None):
        self.x_api_key = settings.X_API_KEY
        self._client = httpx.AsyncClient(
            follow_redirects=True, timeout=10.0, headers={"x-api-key": self.x_api_key}
        )
        self.HOST = settings.HOST
        if async_retry is not None:
            self.async_retry = async_retry
        else:
            self.async_retry = AsyncRetry()

    async def request_url(
        self, method: str, url: str, endpoint: str, json_data: dict | None = None
    ):
        async def request():
            start_time = time.monotonic()
            response = await self._client.request(method, url, json=json_data)
            duration = time.monotonic() - start_time

            events_provider_requests_total.labels(
                endpoint=endpoint, status=response.status_code
            ).inc()

            events_provider_request_duration_seconds.labels(endpoint=endpoint).observe(
                duration
            )

            response.raise_for_status()
            return response.json()

        try:
            return await self.async_retry.execute(request)
        except httpx.ReadTimeout:
            logger.error("Timeout while requesting {}", url)
            raise
        except httpx.HTTPError as e:
            logger.error("HTTP error while requesting {} {}: {}", method, url, e)
            raise

        except Exception as e:
            logger.error("Unexpected error while requesting {} {}: {}", method, url, e)
            raise

    async def get_seats(self, event_id: UUID):
        url = f"{self.HOST}/api/events/{event_id}/seats"
        result = await self.request_url("GET", url, "/seats")
        return result["seats"]

    async def cancel_registration(self, event_id: UUID, ticket_id: UUID):
        url = f"{self.HOST}/api/events/{event_id}/unregister"
        return await self.request_url(
            "DELETE", url, "/unregister", {"ticket_id": str(ticket_id)}
        )

    async def register(self, registration_info: RegistrationInfoIn):
        url = f"{self.HOST}/api/events/{registration_info.event_id}/register/"
        json_data = registration_info.model_dump()
        json_data.pop("event_id", None)
        json_data.pop("idempotency_key", None)
        return await self.request_url("POST", url, "/register", json_data=json_data)
