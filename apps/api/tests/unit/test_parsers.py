"""Parser fallback tests."""

from lra_api.services.ingestion.parsers import parse_bytes


def test_parse_txt_content() -> None:
    text = "Hello from parser"
    output = parse_bytes(text.encode("utf-8"), filename="sample.txt", mime_type="text/plain")
    assert "Hello" in output


def test_parse_csv_content() -> None:
    csv = "col1,col2\n1,2\n3,4"
    output = parse_bytes(csv.encode("utf-8"), filename="sample.csv", mime_type="text/csv")
    assert "col1" in output
    assert "3, 4" in output
