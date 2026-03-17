import json
from uuid import UUID

import httpx

from app.core.config import settings
from app.modules.clients.async_retry import AsyncRetry
from app.modules.tickets.schemas import RegistrationInfoIn


class AsyncEventsProviderClient:
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

    async def get_url(self, url: str) -> json:
        async def request():
            response = await self._client.get(url)
            response.raise_for_status()
            return response.json()

        return await self.async_retry.execute(request)

    async def post_url(self, url: str, json_data: dict | None = None) -> json:
        async def request():
            response = await self._client.post(url, json=json_data)
            response.raise_for_status()
            return response.json()

        return await self.async_retry.execute(request)

    async def get_seats(self, event_id: UUID):
        url = f"{self.HOST}/api/events/{event_id}/seats"
        result = await self.get_url(url)
        return result["seats"]


class EventsProviderClient:
    events: list | None

    def __init__(self, async_retry: AsyncRetry | None = None):
        self.x_api_key = settings.X_API_KEY
        self._client = httpx.Client(
            follow_redirects=True, timeout=10.0, headers={"x-api-key": self.x_api_key}
        )
        self.HOST = settings.HOST
        if async_retry is not None:
            self.async_retry = async_retry
        else:
            self.async_retry = AsyncRetry()

    async def post_url(self, url: str, json_data: dict | None = None) -> json:
        async def request():
            response = self._client.post(url, json=json_data)
            response.raise_for_status()
            return response.json()

        return await self.async_retry.execute(request)

    async def register(self, registration_info: RegistrationInfoIn):
        url = f"{self.HOST}/api/events/{registration_info.event_id}/register/"
        json_data = registration_info.model_dump()
        json_data.pop("event_id", None)
        return await self.post_url(url, json_data=json_data)
