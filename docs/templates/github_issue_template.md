---
title: "Implement Feature: [Feature Name] (ID: [Feature ID])"
---

## Feature Information
- **ID**: [Feature ID]
- **Name**: [Feature Name]
- **Category**: [Category]
- **Complexity**: [1-5]

## Implementation Requirements
- [ ] Create implementation file at `src/features/[category]/[Feature ID]_[feature_name].py`
- [ ] Calculate feature for all teams/seasons
- [ ] Add unit tests at `tests/features/[category]/test_[Feature ID]_[feature_name].py`
- [ ] Update FEATURES.md status
- [ ] Create documentation file at `docs/features/[category]/[Feature ID]_[feature_name].md`

## Technical Details
[Details on data sources, calculation approach, performance considerations, etc.]

## Definition
[Mathematical definition or explanation]

## Acceptance Criteria

### Feature Implementation
- [ ] Feature is calculated correctly for all teams/seasons
- [ ] Unit tests pass and achieve at least 90% code coverage
- [ ] Documentation is complete and follows the template
- [ ] FEATURES.md status is updated to reflect implementation status
- [ ] Code follows project coding standards
- [ ] Performance is acceptable for dataset size

### PR Preparation (Required Before Submission)
- [ ] **Step 1: Comprehensive Testing**
  - [ ] All tests pass (run `python -m pytest`)

- [ ] **Step 2: Code Linting**
  - [ ] Code passes linting with no warnings or errors (run `ruff check .`)
  - [ ] No linting exceptions or `# noqa` comments added

- [ ] **Step 3: End-to-End Validation**
  - [ ] Pipeline runs successfully with existing data (run `python run_pipeline.py`)
  - [ ] Pipeline runs successfully with clean data (run `python run_pipeline.py --clean-all`)
  - [ ] Final verification passes (run `pytest`, `ruff check .`, and `python run_pipeline.py`)

## Related Features
- [Feature ID] [Feature Name]: [Brief description of relationship]

## Resources
- [Links to reference implementations, papers, or other resources] 