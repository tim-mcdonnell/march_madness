"""Configuration file for pytest.

This file contains settings and fixtures for all tests.
"""

import os

# Disable efficiency features during most tests to speed up test runs
# This prevents the slow efficiency metrics code from being imported and registered
# The specific efficiency feature tests will re-enable as needed
os.environ["ENABLE_EFFICIENCY_FEATURES"] = "0" 