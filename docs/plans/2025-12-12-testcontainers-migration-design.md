# Testcontainers Migration Design

## Overview

Replace docker-compose with testcontainers-python for running Kroki in tests. Tests skip gracefully when Docker isn't available.

## Changes

### 1. Add dependency (`pyproject.toml`)

Add to `[project.optional-dependencies]` tests section:
```
testcontainers[generic]
```

### 2. Create fixture (`unittests/conftest.py`)

```python
import pytest
from rebdhuhn.kroki import Kroki

try:
    from testcontainers.generic import GenericContainer
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


@pytest.fixture(scope="session")
def kroki_container():
    """
    Start a Kroki container for the entire test session.
    Skips if Docker is not available.
    """
    if not is_docker_available():
        pytest.skip("Docker is not available - skipping Kroki tests")

    container = GenericContainer("yuzutech/kroki:0.24.1")
    container.with_exposed_ports(8000)
    container.start()

    yield container

    container.stop()


@pytest.fixture(scope="session")
def kroki_client(kroki_container) -> Kroki:
    """Provides a Kroki client configured to use the testcontainer."""
    host = kroki_container.get_container_host_ip()
    port = kroki_container.get_exposed_port(8000)
    return Kroki(kroki_host=f"http://{host}:{port}")
```

### 3. Update test files

Update these tests to use `kroki_client` fixture:

- `test_table_to_graph.py`:
  - `test_table_to_digraph`
  - `test_table_to_digraph_dot_real_kroki_request`
  - `test_table_to_digraph_dot_with_watermark_real_kroki_request`
  - `test_empty_table_to_graph`
  - `test_table_to_dot_to_svg`
  - `InterceptedKrokiClient.__init__` - accept `kroki_host` parameter
  - `create_and_save_svg_test` - receive client as parameter

- `test_e0055.py`: `test_e0055_svg_creation`
- `test_malo_ident.py`: `test_e0594_svg_creation`
- `test_transitional_outcome.py`: `test_e0610_svg_creation`

Mocked tests remain unchanged.

### 4. Delete files

- `docker-compose.yaml`

### 5. Update README.md

Remove docker-compose setup instructions (lines ~130-143). Replace with:

```markdown
First, make sure to have Docker installed and running. The tests use testcontainers to automatically start a Kroki instance when needed.
```

## Behavior

- Container starts once per test session (session-scoped fixture)
- Tests skip gracefully when Docker isn't available
- Mocked tests continue to work without Docker
