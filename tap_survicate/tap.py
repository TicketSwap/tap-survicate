"""Survicate tap class."""

from __future__ import annotations

import sys

import requests
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

    def _fetch_all_surveys(self) -> list[dict]:
        url: str | None = "https://data-api.survicate.com/v2/surveys"
        headers = {"Authorization": f"Basic {self.config['api_key']}"}
        survey_ids_filter: list[str] | None = self.config.get("survey_ids")
        all_surveys: list[dict] = []

        while url:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            body = response.json()
            all_surveys.extend(body.get("data", []))
            next_url = body.get("pagination_data", {}).get("next_url")
            url = next_url if next_url != url else None

        if survey_ids_filter is not None:
            all_surveys = [s for s in all_surveys if s.get("id") in survey_ids_filter]

        return all_surveys

    @override
    def discover_streams(self) -> list[streams.SurvicateStream]:
        """Return a list of discovered streams — one responses stream per survey."""
        discovered: list[streams.SurvicateStream] = [streams.SurveysStream(self)]
        for survey in self._fetch_all_surveys():
            stream_cls = streams.build_survey_responses_stream(survey["id"])
            discovered.append(stream_cls(self))
        return discovered


if __name__ == "__main__":
    TapSurvicate.cli()
