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


def _build_test_class() -> type:
    """Return the live SDK test suite, or a skipped placeholder without a key.

    The Survicate API has no sandbox, so the standard SDK suite is a live
    integration test. It runs when TAP_SURVICATE_API_KEY is available and is
    skipped otherwise (e.g. CI without the secret) rather than failing.
    """
    if API_KEY:
        return get_tap_test_class(tap_class=TapSurvicate, config=SAMPLE_CONFIG)

    @pytest.mark.skip(reason="TAP_SURVICATE_API_KEY not set; skipping live integration tests")
    class _SkippedTapSurvicate:
        """Placeholder skipped when no API key is available."""

    return _SkippedTapSurvicate


TestTapSurvicate = _build_test_class()
