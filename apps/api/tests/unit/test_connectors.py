"""Connector utility tests."""

from lra_api.services.ingestion.connectors import ConnectorService


def test_vtt_to_text_removes_timestamps() -> None:
    vtt = """WEBVTT

00:00:00.000 --> 00:00:02.000
Hello world

00:00:02.000 --> 00:00:04.000
AI research
"""
    text = ConnectorService._vtt_to_text(vtt)

    assert "-->" not in text
    assert "Hello world" in text
    assert "AI research" in text
