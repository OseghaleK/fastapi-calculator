"""Starts a real server so the browser tests have something to visit."""

import socket
import subprocess
import sys
import time

import pytest

HOST = "127.0.0.1"
PORT = 8765
BASE_URL = f"http://{HOST}:{PORT}"


def _wait_for_server(timeout=30):
    """Poll the port until the server answers, or give up."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket() as probe:
            if probe.connect_ex((HOST, PORT)) == 0:
                return True
        time.sleep(0.3)
    return False


@pytest.fixture(scope="session")
def live_server():
    """Run uvicorn for the length of the test session."""
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app",
         "--host", HOST, "--port", str(PORT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if not _wait_for_server():
        process.terminate()
        pytest.fail("The server did not start in time.")
    yield BASE_URL
    process.terminate()
    process.wait(timeout=10)
