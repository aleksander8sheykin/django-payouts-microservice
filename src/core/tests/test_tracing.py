import pytest

from core import tracing


def test_get_trace_id_default():
    assert tracing.get_trace_id() == tracing.TRACE_ID_DEFAULT


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("aabbccdd", "aabbccdd"),
        ("ABC-123", "abc-123"),
        ("  abc-123  ", "abc-123"),
    ],
)
def test_normalize_trace_id_valid(raw, expected):
    assert tracing.normalize_trace_id(raw) == expected


@pytest.mark.parametrize("raw", ["", "   ", "***", "a" * 65])
def test_normalize_trace_id_invalid(raw):
    assert tracing.normalize_trace_id(raw) is None


def test_ensure_trace_id_generates_when_invalid():
    trace_id = tracing.ensure_trace_id("***")
    assert trace_id
    assert trace_id != "***"
    assert len(trace_id) == 32
