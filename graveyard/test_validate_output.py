from io import StringIO

from validate_output import OutputValidator, TeeStream, console


def test_teestream_write_and_flush():
    main_stream = StringIO()
    capture_stream = StringIO()
    tee_stream = TeeStream(main_stream, capture_stream)
    test_data = "Hello, World!"
    tee_stream.write(test_data)
    tee_stream.flush()
    assert main_stream.getvalue() == test_data
    assert capture_stream.getvalue() == test_data


def test_outputvalidator_capture_output():
    validator = OutputValidator()
    print("Test output")
    validator.stop()
    captured_output = validator.captured_output.getvalue().strip()
    assert captured_output == "Test output"


def test_outputvalidator_eq():
    validator = OutputValidator()
    print("Expected output")
    validator.stop()
    # Compare captured output to expected output
    assert validator == "Expected output"


def test_console_global():
    console.start()  # Ensure the capture starts
    print("Global console test")
    console.stop()  # Ensure the capture stops before the assertion
    assert console == "Global console test"
    console.start()  # Restart the capture for any subsequent tests
