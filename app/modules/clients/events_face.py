import json
from uuid import UUID

import httpx

from app.core.config import settings
from app.modules.clients.retry_config import RetryConfig


class EventsProviderClient:
    _client: httpx.AsyncClient
    HOST = settings.HOST
    x_api_key: str = settings.X_API_KEY
    events: list | None
    retry_config: RetryConfig

    def __init__(self):
        self._client = httpx.AsyncClient(
            follow_redirects=True, timeout=10.0, headers={"x-api-key": self.x_api_key}
        )
        self.retry_config = RetryConfig()

    async def get_url(self, url: str) -> json:

        last_error = None

        for _ in range(
            self.retry_config.max_retries
        ):  # Доделать экспонициальную задержку
            try:
                response = await self._client.get(url)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code not in self.retry_config.retryable_statuses:
                    error_msg = (
                        f"HTTP error {exc.response.status_code}: {exc.response.text}"
                    )
                    raise ValueError(
                        f"External service returned error: {error_msg}"
                    ) from exc
                last_error = exc
            except (httpx.TimeoutException, httpx.ConnectError) as exc:
                last_error = exc
            except httpx.RequestError as exc:
                # Общие ошибки запроса
                last_error = exc
        raise ValueError(
            f"Couldn't get {url} after {self.retry_config.max_retries} attempts"
        ) from last_error

    async def get_seats(self, event_id: UUID):
        url = f"http://{self.HOST}/api/events/{event_id}/seats"
        result = await self.get_url(url)
        return result["seats"]
