# Testing Standards

This document outlines the standards for testing in the NCAA March Madness Predictor project. Following these standards ensures that our code is reliable, maintainable, and produces accurate results.

## 1. Testing Philosophy

Our testing approach is guided by these core principles:

1. **Correctness**: Tests verify that code works as intended
2. **Completeness**: Tests cover all critical paths and edge cases
3. **Data Quality**: Tests verify data integrity at every stage
4. **Isolation**: Tests are independent and don't interfere with each other
5. **Maintainability**: Tests are clear, concise, and easy to update

## 2. Test Types and Organization

### 2.1 Test Types

| Test Type | Purpose | Location | Scope |
|-----------|---------|----------|-------|
| **Unit Tests** | Test individual functions and methods | `tests/unit/` | Single function or class |
| **Integration Tests** | Test component interactions | `tests/integration/` | Multiple components |
| **Data Quality Tests** | Test data integrity | `tests/data_quality/` | Data validation |
| **End-to-End Tests** | Test complete workflows | `tests/e2e/` | Full system |
| **Regression Tests** | Prevent regressions | `tests/regression/` | Known issues |
| **Performance Tests** | Test system performance | `tests/performance/` | Speed and efficiency |

### 2.2 Test File Organization

- Test files should mirror the structure of the source code
- Test file names should follow the pattern `test_[module_name].py`
- Test class names should follow the pattern `Test[ClassUnderTest]`
- Test function names should follow the pattern `test_[function_under_test]_[scenario]`

Example:
```
src/
  features/
    team_performance/
      win_percentage.py

tests/
  unit/
    features/
      team_performance/
        test_win_percentage.py
```

## 3. Test Coverage Requirements

### 3.1 Minimum Coverage

| Component Type | Minimum Line Coverage | Minimum Branch Coverage |
|----------------|----------------------|-------------------------|
| Core Data Pipeline | 90% | 85% |
| Feature Calculations | 95% | 90% |
| API Client | 90% | 85% |
| Models | 85% | 80% |
| Utilities | 80% | 75% |

### 3.2 Required Coverage Areas

All components must have tests that cover:

1. **Normal Operation**: Test typical use cases
2. **Edge Cases**: Test boundary conditions
3. **Error Handling**: Test error conditions
4. **Input Validation**: Test with valid and invalid inputs

### 3.3 Critical Paths

These paths must have 100% test coverage:

1. Data validation logic
2. Feature calculation core algorithms
3. Data transformations
4. Model prediction code

## 4. Data Quality Testing

### 4.1 Schema Validation Tests

All data must have tests that verify:

1. Required columns exist
2. Column data types are correct
3. Primary key constraints are enforced
4. Foreign key relationships are maintained

### 4.2 Data Integrity Tests

Data transformations must have tests that verify:

1. No unexpected NULL values
2. No duplicate records
3. Values are within valid ranges
4. Aggregations are mathematically correct
5. No data is lost during transformation

### 4.3 Data Completeness Tests

Data sources must have tests that verify:

1. All expected records are present
2. No unexpected gaps in time series data
3. Relationships are fully represented

### 4.4 Example Data Quality Test

```python
def test_win_percentage_data_quality():
    """Test that win percentage feature produces valid data."""
    # Calculate feature
    win_pct_df = calculate_win_percentage(sample_games_df)
    
    # 1. Schema validation
    assert "team_id" in win_pct_df.columns
    assert "season" in win_pct_df.columns
    assert "win_percentage" in win_pct_df.columns
    
    # 2. Data integrity
    # No NULL values in key columns
    assert win_pct_df["team_id"].isna().sum() == 0
    assert win_pct_df["win_percentage"].isna().sum() == 0
    
    # Values in valid range
    assert (win_pct_df["win_percentage"] >= 0).all()
    assert (win_pct_df["win_percentage"] <= 1).all()
    
    # 3. Completeness
    # All teams are represented
    teams_in_games = sample_games_df["team_id"].unique()
    teams_in_result = win_pct_df["team_id"].unique()
    assert set(teams_in_games) == set(teams_in_result)
```

## 5. Test Implementation Standards

### 5.1 Test Structure

Each test should follow the Arrange-Act-Assert pattern:

```python
def test_function_name_scenario():
    # Arrange - set up test data and conditions
    input_data = ...
    
    # Act - call the function being tested
    result = function_under_test(input_data)
    
    # Assert - verify the result
    assert result == expected_result
```

### 5.2 Test Fixtures

Use pytest fixtures for common setup and teardown:

```python
@pytest.fixture
def sample_games_data():
    """Fixture providing sample games data for testing."""
    return pd.DataFrame({
        "game_id": [1, 2, 3, 4],
        "team_id": [101, 102, 101, 102],
        "opponent_team_id": [102, 101, 103, 103],
        "team_score": [75, 70, 80, 65],
        "opponent_score": [70, 75, 60, 90],
        "team_winner": [True, False, True, False]
    })
```

### 5.3 Parameterized Tests

Use parameterization for testing multiple scenarios:

```python
@pytest.mark.parametrize("games_played,wins,expected_win_pct", [
    (10, 5, 0.5),
    (10, 0, 0.0),
    (10, 10, 1.0),
    (0, 0, 0.0)  # Edge case: no games played
])
def test_win_percentage_calculation(games_played, wins, expected_win_pct):
    """Test win percentage calculation with various scenarios."""
    # Implementation
```

### 5.4 Mocking

Use mocking for testing components with external dependencies:

```python
@patch("src.api.client.requests.get")
def test_api_client_handles_errors(mock_get):
    # Configure mock
    mock_get.side_effect = requests.exceptions.ConnectionError
    
    # Test error handling
    client = APIClient()
    result = client.get_data()
    
    # Verify error handling
    assert result is None
```

## 6. Test Data Management

### 6.1 Test Data Sources

Use these sources for test data, in order of preference:

1. **Generated Test Data**: Programmatically generated data
2. **Small Fixed Datasets**: Small, fixed datasets committed to the repository
3. **Anonymized Real Data**: Real data with sensitive information removed

### 6.2 Test Database

For database integration tests:

1. Use an in-memory DuckDB instance
2. Initialize schema before each test
3. Populate with known test data
4. Clean up after tests

```python
@pytest.fixture
def test_db():
    """Fixture providing a test database."""
    # Create in-memory DB
    conn = duckdb.connect(":memory:")
    
    # Initialize schema
    conn.execute("CREATE TABLE teams (team_id INTEGER, team_name VARCHAR)")
    
    # Add test data
    conn.execute("INSERT INTO teams VALUES (1, 'Team A'), (2, 'Team B')")
    
    yield conn
    
    # Clean up
    conn.close()
```

## 7. Test Execution

### 7.1 Running Tests

Tests should be executable using pytest:

```bash
# Run all tests
pytest

# Run specific test type
pytest tests/unit/

# Run specific test file
pytest tests/unit/features/test_win_percentage.py

# Run specific test
pytest tests/unit/features/test_win_percentage.py::test_win_percentage_calculation
```

### 7.2 Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_function():
    # Test implementation

@pytest.mark.slow
def test_slow_function():
    # Slow test implementation
```

### 7.3 Continuous Integration

Tests will be run automatically on:

1. Every pull request
2. Every push to main branch
3. Nightly builds

## 8. Test-Driven Development

For new features, follow TDD principles:

1. Write test first, defining expected behavior
2. Run the test to verify it fails
3. Implement the feature
4. Run the test to verify it passes
5. Refactor as needed, ensuring tests continue to pass

## 9. Testing Responsibilities

### 9.1 Developer Testing Responsibilities

Developers are responsible for:

1. Writing unit tests for all code they create
2. Writing integration tests for component interactions
3. Ensuring all tests pass before submitting code
4. Updating tests when changing existing code

### 9.2 Code Review Testing Requirements

During code review, reviewers must verify:

1. Tests follow these standards
2. Tests cover all critical paths
3. Tests verify both positive and negative cases
4. Tests include appropriate data quality checks

## 10. Test Documentation

### 10.1 Test Documentation Requirements

All test files must include:

1. Module-level docstring explaining test purpose
2. Function-level docstrings explaining test scenarios
3. Clear comments for complex test logic

### 10.2 Example Test Documentation

```python
"""
Tests for the win percentage feature calculation.

These tests verify that win percentages are calculated correctly
for teams based on their game results.
"""

def test_win_percentage_calculation_standard_case():
    """
    Test win percentage calculation for standard case.
    
    Given a team with a mix of wins and losses,
    When calculating win percentage
    Then the result should be (wins / games_played)
    """
    # Test implementation
```

## 11. Test Review Checklist

Use this checklist when reviewing tests:

- [ ] Tests follow the standard structure and naming conventions
- [ ] Tests cover normal operation, edge cases, and error conditions
- [ ] Tests verify data quality aspects
- [ ] Tests are independent and don't interfere with each other
- [ ] Tests use appropriate fixtures and parameterization
- [ ] Tests are well-documented
- [ ] Tests run efficiently
- [ ] Tests verify the correct behavior, not just the current implementation 