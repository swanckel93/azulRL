import pytest
from azul.tile import TileGenerator


@pytest.fixture(scope="function")
def tg() -> TileGenerator:
    return TileGenerator()
