import json
from uuid import UUID

import httpx

from app.core.config import settings
from app.modules.clients.async_retry import AsyncRetry


class EventsProviderClient:
    HOST = settings.HOST
    x_api_key: str = settings.X_API_KEY
    events: list | None

    def __init__(self, async_retry: AsyncRetry | None = None):
        self._client = httpx.AsyncClient(
            follow_redirects=True, timeout=10.0, headers={"x-api-key": self.x_api_key}
        )
        if async_retry is not None:
            self.async_retry = async_retry
        else:
            self.async_retry = AsyncRetry()

    async def get_url(self, url: str) -> json:
        async def request():
            response = await self._client.get(url)
            response.raise_for_status()
            return response.json()

        return await self.async_retry.execute(request)

    async def get_seats(self, event_id: UUID):
        url = f"http://{self.HOST}/api/events/{event_id}/seats"
        result = await self.get_url(url)
        return result["seats"]
