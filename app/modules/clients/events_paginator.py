from datetime import datetime

from app.modules.clients.events_face import EventsProviderClient


class EventsPaginator:
    def __init__(self, client: EventsProviderClient, date: datetime):
        self.client = client
        self.date = date.strftime("%Y-%m-%d")

    async def __aiter__(self):
        response = await self.client.get_event(
            f"http://{self.client.HOST}/api/events/?changed_at={self.date}"
        )
        yield response
        while True:
            if response["next"] is None:
                break
            response = await self.client.get_event(response["next"])
            yield response
