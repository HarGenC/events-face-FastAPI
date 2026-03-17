from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import httpx
import pytest

from app.core.config import settings
from app.modules.clients.async_retry import AsyncRetry
from app.modules.clients.events_face import EventsProviderClient


class TestEventsFaceClient:
    @pytest.mark.asyncio
    async def test_get_seats(self):
        fake_event_id = uuid4()
        expected_response = {
            "seats": [
                "E103",
                "B65",
                "B191",
                "D309",
                "A43",
                "E357",
                "C106",
                "A2",
                "E160",
                "D80",
                "B95",
                "E335",
                "E147",
                "C65",
                "D178",
            ]
        }
        async_mock_execute = AsyncMock(return_value=expected_response)
        with patch(
            "app.modules.clients.events_face.AsyncRetry.execute", async_mock_execute
        ):
            client = EventsProviderClient()
            seats = await client.get_seats(fake_event_id)

        assert seats == expected_response["seats"]

    @pytest.mark.asyncio
    async def test_get_url(self):
        changed_at = "2027-01-01"
        url = f"http://{settings.HOST}/api/events/?changed_at={changed_at}"
        expected_response = {"next": None, "previous": None, "results": []}

        with patch(
            "app.modules.clients.events_face.httpx.AsyncClient.get",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = expected_response
            mock_response.raise_for_status.return_value = 200

            mock_get.return_value = mock_response

            client = EventsProviderClient()
            result = await client.get_url(url)

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_get_url_with_retry_success(self):
        url = "http://test"
        expected_response = {"status": "ok"}

        mock_get = AsyncMock()

        success_response = Mock()
        success_response.json.return_value = expected_response
        success_response.raise_for_status.return_value = 200

        error = httpx.HTTPStatusError(
            "Service Unavailable", request=Mock(), response=Mock(status_code=503)
        )

        mock_get.side_effect = [error, error, success_response]

        with patch("app.modules.clients.events_face.httpx.AsyncClient.get", mock_get):
            client = EventsProviderClient(async_retry=AsyncRetry(max_retries=3))
            result = await client.get_url(url)

        assert result == expected_response
        assert mock_get.call_count == 3
