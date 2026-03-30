from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.modules.clients.events_face import EventsProviderClient
from app.modules.clients.events_paginator import EventsPaginator


class TestEventsPaginator:
    @pytest.mark.asyncio
    async def test_get_url_with_retry_success(self):

        client = EventsProviderClient()
        client.request_url = AsyncMock()

        first_response = {
            "next": "http://example.com/api/events/?changed_at=2000-01-01&cursor=cD0yMDI2LTAzLTMwKzEyJTNBMTAlM0EwMC41MDE4OTMlMkIwMCUzQTAw",
            "previous": None,
            "results": [],
        }
        second_response = {
            "next": "http://example.com/api/events/?changed_at=2000-01-01&cursor=cD0yMDI2LRAzLTMw4zEyJTNBMTAlM5EwMC41MDE4STMNMkIwMCAzQTGw",
            "previous": None,
            "results": [],
        }
        last_response = {"next": None, "previous": None, "results": []}

        client.request_url.side_effect = [
            first_response,
            second_response,
            last_response,
        ]

        events_paginator = EventsPaginator(client, datetime.fromisoformat("2000-01-01"))
        results = []
        async for page in events_paginator:
            results.append(page)

        assert len(results) == 3
        assert client.request_url.call_count == 3
