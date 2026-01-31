# Test Suite Documentation

This directory contains comprehensive unit tests for the Supermarket Simulation project.

## Test Structure

### Test Files

- `test_product.py` - Tests for the Product class
- `test_shopmap.py` - Tests for the ShopMap class  
- `test_statemap.py` - Tests for the StateMap class
- `test_agent.py` - Tests for the Agent class
- `test_maze_solver.py` - Tests for the AgentPathfinder class
- `test_simulation.py` - Tests for the Simulation class
- `conftest.py` - Pytest configuration and shared fixtures

### Test Categories

Each test file contains the following categories:

1. **Smoke Tests** - Basic instantiation and functionality checks
2. **Unit Tests** - Detailed testing of individual methods and properties
3. **Integration Tests** - Testing interactions between components
4. **Edge Cases** - Testing boundary conditions and error handling

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_product.py
```

### Run with Verbose Output
```bash
pytest tests/ -v
```

### Run with Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### Run Specific Test Class
```bash
pytest tests/test_product.py::TestProductSmoke
```

### Run Specific Test Method
```bash
pytest tests/test_product.py::TestProductSmoke::test_product_creation
```

## Configuration Files

Tests use the following configuration files:
- `configs/empty.yaml` - Empty supermarket layout
- `configs/surround.yaml` - Supermarket with surrounding walls and aisles

## Requirements

Install test dependencies:
```bash
pip install pytest pytest-cov
```

## Test Coverage

The test suite aims to cover:
- All public methods and properties
- Initialization and configuration
- State management and updates
- Pathfinding algorithms
- Visualization functions
- Error handling and edge cases

## Adding New Tests

When adding new tests:
1. Follow the existing naming convention: `test_<module>.py`
2. Organize tests into classes by functionality
3. Use descriptive test method names: `test_<what_is_being_tested>`
4. Add docstrings explaining what each test verifies
5. Use both config files (empty.yaml and surround.yaml) where applicable
6. Include smoke tests for basic functionality
7. Add integration tests for component interactions

## Common Patterns

### Setup a basic test
```python
def test_something(self):
    """Test that something works."""
    # Arrange
    obj = MyClass()
    
    # Act
    result = obj.do_something()
    
    # Assert
    assert result is not None
```

### Using fixtures
```python
def test_with_config(self, empty_config):
    """Test using config fixture."""
    shop = ShopMap(empty_config)
    assert shop is not None
```

### Testing exceptions
```python
def test_raises_error(self):
    """Test that error is raised."""
    with pytest.raises(ValueError):
        obj.invalid_operation()
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. Ensure all tests pass before committing changes.
