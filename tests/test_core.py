"""Tests standard tap features using the built-in SDK tests library."""

import os

import pytest
from singer_sdk.testing import get_tap_test_class

from tap_survicate.tap import TapSurvicate

API_KEY = os.environ.get("TAP_SURVICATE_API_KEY")

SAMPLE_CONFIG = {
    "api_key": API_KEY or "",
    # No survey_ids filter: the integration test syncs whatever surveys the
    # configured account exposes, so it is independent of any one workspace.
    # Production scoping to CSAT/NPS survey_ids lives in data-transformations.
}

pytestmark = pytest.mark.skipif(
    not API_KEY,
    reason="TAP_SURVICATE_API_KEY not set; skipping live integration tests",
)

TestTapSurvicate = get_tap_test_class(tap_class=TapSurvicate, config=SAMPLE_CONFIG)
