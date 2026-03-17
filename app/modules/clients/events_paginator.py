from datetime import datetime

from app.modules.clients.events_face import AsyncEventsProviderClient


class EventsPaginator:
    def __init__(self, client: AsyncEventsProviderClient, date: datetime):
        self.client = client
        self.date = date.strftime("%Y-%m-%d")

    async def __aiter__(self):
        response = await self.client.get_url(
            f"{self.client.HOST}/api/events/?changed_at={self.date}"
        )
        yield response
        while True:
            if response["next"] is None:
                break
            response = await self.client.get_url(response["next"])
            yield response
