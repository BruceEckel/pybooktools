#: test_validate_output.py
import sys
from io import StringIO

import pytest

from src.pybooktools.validate_output import OutputValidator, TeeStream


@pytest.fixture
def tee_stream():
    main_stream = StringIO()
    capture_stream = StringIO()
    return TeeStream(main_stream, capture_stream)


def test_tee_stream_write(tee_stream):
    data = "test"

    tee_stream.write(data)

    assert tee_stream.main_stream.getvalue() == data
    assert tee_stream.capture_stream.getvalue() == data


def test_tee_stream_flush(tee_stream):
    data = "test"
    tee_stream.write(data)

    # initial streams objects wouldn't have this method
    tee_stream.main_stream.flush = lambda: setattr(
        tee_stream.main_stream, "flushed", True
    )
    tee_stream.capture_stream.flush = lambda: setattr(
        tee_stream.capture_stream, "flushed", True
    )

    tee_stream.flush()

    assert hasattr(tee_stream.main_stream, "flushed")
    assert hasattr(tee_stream.capture_stream, "flushed")


class TestOutputValidator:

    def test_start(self, capsys):
        ov = OutputValidator()
        print("test")
        captured = capsys.readouterr()
        assert captured.out == "test\n"

    def test_stop(self, monkeypatch):
        ov = OutputValidator()
        monkeypatch.setattr(sys, "stdout", ov.original_stdout)
        monkeypatch.setattr(sys, "stderr", ov.original_stderr)
        assert sys.stdout == ov.original_stdout
        assert sys.stderr == ov.original_stderr

    # def test_eq(self, monkeypatch):
    #     ov1 = OutputValidator()
    #     ov2 = OutputValidator()
    #     monkeypatch.setattr(ov1, "captured_output", StringIO("test"))
    #     monkeypatch.setattr(ov2, "captured_output", StringIO("test"))
    #     assert ov1 == ov2
