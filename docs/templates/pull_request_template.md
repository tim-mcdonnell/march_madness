# Pull Request Template

## Summary
<!-- Provide a brief summary of the changes introduced by this PR -->

## Issue
<!-- Link to the issue this PR addresses, if applicable, or a description of the problem solved -->
Fixes #[Issue Number]

## Solution
<!-- Describe the solution you designed and how it functions. -->

## Results
<!-- Compare/contrast the before & after of this PR.  Be quantitative if possible. -->

## Changes
<!-- List the specific changes made in this PR -->
- 
- 
- 

## Type of Change
<!-- Mark the types of changes introduced in this PR -->
- [ ] Bug fix (non-breaking change addressing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Code refactor (code improvements without changing behavior)
- [ ] Documentation update
- [ ] Test improvements

## Validation Steps
<!-- Describe the testing process you've followed to validate your changes -->
### PR Preparation (Required Before Submission)
- [ ] **Step 1: Comprehensive Testing**
  - [ ] All tests pass (`python -m pytest`)

- [ ] **Step 2: Code Linting**
  - [ ] Code passes linting with no warnings or errors (`ruff check .`)
  - [ ] No linting exceptions or `# noqa` comments added

- [ ] **Step 3: End-to-End Validation**
  - [ ] Pipeline runs successfully with existing data (`python run_pipeline.py`)
  - [ ] Pipeline runs successfully with clean data (`python run_pipeline.py --clean-all`)
  - [ ] Final verification passes (`pytest`, `ruff check .`, and `python run_pipeline.py`)

## Additional Context
<!-- Add any other context about the PR here including future considerations.m-->
