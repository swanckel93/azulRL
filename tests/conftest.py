import pytest
import random

from azul.data_model import TileType
from azul.components import Tile


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")


def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on patterns if not explicitly marked."""
    for item in items:
        # Get existing markers
        markers = [marker.name for marker in item.iter_markers()]

        # Skip if already marked
        if "unit" in markers or "integration" in markers:
            continue

        # Auto-mark based on class/function name patterns
        if "integration" in item.name.lower() or "Integration" in str(item.cls):
            item.add_marker(pytest.mark.integration)
        elif "unit" in item.name.lower() or any(
            cls_name in str(item.cls)
            for cls_name in [
                "TestTile",
                "TestContainer",
                "TestBag",
                "TestFactory",
                "TestPatternLine",
                "TestPlayerBoard",
                "TestAction",
            ]
        ):
            item.add_marker(pytest.mark.unit)
        else:
            # Default to unit test if uncertain
            item.add_marker(pytest.mark.unit)


# Global fixtures that might be useful across tests
@pytest.fixture
def sample_tiles():
    """Fixture providing a standard set of tiles for testing."""
    return [
        Tile(TileType.BLUE),
        Tile(TileType.RED),
        Tile(TileType.YELLOW),
        Tile(TileType.BLACK),
        Tile(TileType.WHITE),
    ]


@pytest.fixture
def deterministic_shuffle(monkeypatch):
    """Fixture that makes random.shuffle deterministic for testing."""

    def mock_shuffle(lst):
        # Don't shuffle - keep original order for deterministic tests
        pass

    monkeypatch.setattr(random, "shuffle", mock_shuffle)


@pytest.fixture
def no_random_shuffle(monkeypatch):
    """Fixture that disables random.shuffle completely."""

    def identity_shuffle(lst):
        return lst

    monkeypatch.setattr(random, "shuffle", identity_shuffle)


# Pytest configuration options
def pytest_addoption(parser):
    """Add command line options for test filtering."""
    parser.addoption(
        "--run-unit", action="store_true", default=False, help="run unit tests only"
    )
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests only",
    )


def pytest_runtest_setup(item):
    """Skip tests based on command line options."""
    if item.config.getoption("--run-unit"):
        if "integration" in [marker.name for marker in item.iter_markers()]:
            pytest.skip("skipping integration test")
    elif item.config.getoption("--run-integration"):
        if "unit" in [marker.name for marker in item.iter_markers()]:
            pytest.skip("skipping unit test")
