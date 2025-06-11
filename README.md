# azulRL
Toying around with the game azul

# Azul Game Test Suite

This directory contains the refactored test suite for the Azul game, converted from unittest to pytest and organized by scope.

## File Structure

```
tests/
├── conftest.py           # Pytest configuration and shared fixtures
├── pytest.ini           # Pytest settings
├── test_models.py        # Unit tests for basic model classes
├── test_game.py          # Integration tests for game logic
├── test_actions.py       # Integration tests for action validation
└── README_TESTING.md     # This file
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
Located in `test_models.py`, these tests focus on individual components in isolation:

- **TestTile**: Basic tile creation, equality, and hashing
- **TestContainer**: Container operations (add, remove, count tiles)
- **TestBag**: Tile bag initialization and drawing
- **TestFactory**: Factory creation and tile management
- **TestPatternLine**: Pattern line logic and capacity handling
- **TestPlayerBoard**: Player board state and tile placement rules
- **TestAction**: Action object creation and validation

### Integration Tests (`@pytest.mark.integration`)
Spread across `test_game.py` and `test_actions.py`, these test component interactions:

- **TestAzulGame**: Complete game initialization and action execution
- **TestGetValidActions**: Action validation in various game states

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Only Unit Tests
```bash
pytest -m unit
# or
pytest --run-unit
```

### Run Only Integration Tests
```bash
pytest -m integration
# or
pytest --run-integration
```

### Run Tests with Coverage
```bash
pytest --cov=azul_game --cov-report=html
```

### Run Specific Test File
```bash
pytest test_models.py
pytest test_game.py
pytest test_actions.py
```

### Run Specific Test Class
```bash
pytest test_models.py::TestTile
pytest test_game.py::TestAzulGame
```

### Run Specific Test Method
```bash
pytest test_models.py::TestTile::test_tile_creation
```

## Key Changes from unittest

### Assertions
- `self.assertEqual(a, b)` → `assert a == b`
- `self.assertTrue(x)` → `assert x`
- `self.assertFalse(x)` → `assert not x`
- `self.assertIsNone(x)` → `assert x is None`
- `self.assertLessEqual(a, b)` → `assert a <= b`

### Test Structure
- Removed `setUp()` methods in favor of pytest fixtures
- Classes no longer inherit from `unittest.TestCase`
- Added `@pytest.mark.unit` and `@pytest.mark.integration` decorators
