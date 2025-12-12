"""
Pytest fixtures for rebdhuhn tests.
"""

import pytest

from rebdhuhn.kroki import Kroki

try:
    from testcontainers.core.container import DockerContainer

    TESTCONTAINERS_AVAILABLE = True
except ImportError:
    TESTCONTAINERS_AVAILABLE = False


def is_docker_available() -> bool:
    """Check if Docker daemon is running."""
    if not TESTCONTAINERS_AVAILABLE:
        return False
    try:
        import docker

        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


def wait_for_kroki(host: str, port: str, timeout: float = 30.0) -> None:
    """Wait for Kroki to be ready by polling its health endpoint."""
    import time

    import requests

    url = f"http://{host}:{port}/health"
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(0.5)
    raise TimeoutError(f"Kroki did not become ready within {timeout} seconds")


@pytest.fixture(scope="session")
def kroki_container():
    """
    Start a Kroki container for the entire test session.
    Skips if Docker is not available.
    """
    if not is_docker_available():
        pytest.skip("Docker is not available - skipping Kroki tests")

    container = DockerContainer("yuzutech/kroki:0.24.1")
    container.with_exposed_ports(8000)
    container.start()

    # Wait for Kroki to be ready
    host = container.get_container_host_ip()
    port = container.get_exposed_port(8000)
    wait_for_kroki(host, port)

    yield container

    container.stop()


@pytest.fixture(scope="session")
def kroki_client(kroki_container) -> Kroki:
    """Provides a Kroki client configured to use the testcontainer."""
    host = kroki_container.get_container_host_ip()
    port = kroki_container.get_exposed_port(8000)
    return Kroki(kroki_host=f"http://{host}:{port}")
