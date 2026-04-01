import httpx
from loguru import logger

from app.core.config import settings
from app.modules.clients.async_retry import AsyncRetry


class NotificationClient:
    def __init__(self, async_retry: AsyncRetry | None = None):
        self.x_api_key = settings.X_API_KEY
        self._client = httpx.AsyncClient(
            follow_redirects=True, timeout=10.0, headers={"x-api-key": self.x_api_key}
        )
        self.HOST = settings.NOTIFICATION_HOST
        if async_retry is not None:
            self.async_retry = async_retry
        else:
            self.async_retry = AsyncRetry()

    async def request_url(self, method: str, url: str, json_data: dict | None = None):
        async def request():
            response = await self._client.request(method, url, json=json_data)
            response.raise_for_status()
            return response.json()

        try:
            return await self.async_retry.execute(request)
        except httpx.ReadTimeout:
            logger.error("Timeout while requesting {}", url)
            raise
        except httpx.HTTPError as e:
            logger.error("HTTP error while requesting %s %s: %s", method, url, e)
            raise

        except Exception as e:
            logger.error("Unexpected error while requesting %s %s: %s", method, url, e)
            raise

    async def send_notification(self, notification_data: dict):
        url = f"{self.HOST}/api/notifications"
        return await self.request_url("POST", url, json_data=notification_data)
