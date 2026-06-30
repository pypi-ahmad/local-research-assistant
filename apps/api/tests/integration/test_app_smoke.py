"""Integration smoke tests for application assembly."""

from lra_api.main import liveness
from lra_api.services.monitoring.metrics import metrics


async def test_liveness_endpoint_function() -> None:
    payload = await liveness()
    assert payload == {"status": "alive"}


async def test_metrics_endpoint_function() -> None:
    response = await metrics()
    assert response.status_code == 200
    assert "text/plain" in response.media_type
