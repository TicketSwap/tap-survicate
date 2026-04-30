"""Survicate tap class."""

from __future__ import annotations

import sys

from singer_sdk import Tap
from singer_sdk import typing as th

from tap_survicate import streams

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class TapSurvicate(Tap):
    """Singer tap for Survicate."""

    name = "tap-survicate"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType(nullable=False),
            required=True,
            secret=True,
            title="API Key",
            description=(
                "Survicate API key. Find it in the Survicate panel under "
                "Surveys Settings → Access Keys."
            ),
        ),
        th.Property(
            "start_date",
            th.DateTimeType(nullable=True),
            description="The earliest response date to sync (ISO 8601).",
        ),
        th.Property(
            "survey_ids",
            th.ArrayType(th.StringType),
            description=(
                "Optional list of survey IDs to sync. "
                "When set, only surveys whose ID matches an entry in this list "
                "will be synced. When omitted, all surveys are synced."
            ),
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[streams.SurvicateStream]:
        return [
            streams.SurveysStream(self),
            streams.SurveyQuestionsStream(self),
            streams.SurveyResponsesStream(self),
            streams.SurveyQuestionResponsesStream(self),
        ]


if __name__ == "__main__":
    TapSurvicate.cli()
