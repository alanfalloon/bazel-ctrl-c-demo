#!/usr/bin/env python3
"""My example test.

This test spawns a child and creates temporary files. It depends on signal
handlers to clean these up in case of early exit. This is to show why Bazel's
behavior of sending SIGKILL to tests is broken. See README.md for more.

"""
import signal
import subprocess
import tempfile
import time


def signal_handler(signal_num, frame):
    """Raise an exception to gracefully exit."""
    raise RuntimeError(f"Caught signal {signal_num}")


for signal_num in {signal.SIGTERM, signal.SIGINT, signal.SIGHUP}:
    signal.signal(signal_num, signal_handler)

with tempfile.NamedTemporaryFile(dir="/tmp", prefix="ctrl-c-") as temp_file:
    child = subprocess.Popen(
        ["/bin/sh", "-c", "while sleep 1; do echo working ; done"],
        start_new_session=True,
        stdout=temp_file,
    )
    try:
        time.sleep(10)
    finally:
        child.terminate()
    returncode = child.wait()
    assert returncode == -signal.SIGTERM, f"got {returncode}"
    temp_file.seek(0)
    line = temp_file.readline()
    assert line == b"working\n", f"got {line!r}"
print("passed")
