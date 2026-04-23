"""Stream type classes for tap-survicate."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from singer_sdk import typing as th

from tap_survicate.client import SurvivatePaginator, SurvicateStream

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from singer_sdk.helpers.types import Context


class SurveysStream(SurvicateStream):
    """Surveys metadata stream."""

    name = "surveys"
    path = "/surveys"
    primary_keys = ("id",)
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.StringType, required=True),
        th.Property("name", th.StringType),
    ).to_dict()

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        survey_ids: list[str] | None = self.config.get("survey_ids")
        if survey_ids is not None and row.get("id") not in survey_ids:
            return None
        return row


_RESPONSES_SCHEMA = th.PropertiesList(
    th.Property("uuid", th.StringType, required=True),
    th.Property("survey_id", th.StringType),
    th.Property("collected_at", th.DateTimeType),
    th.Property("url", th.StringType),
    th.Property("device_type", th.StringType),
    th.Property("operating_system", th.StringType),
    th.Property("language", th.StringType),
    th.Property("platform", th.StringType),
    th.Property(
        "respondent",
        th.ObjectType(
            th.Property("uuid", th.StringType),
            th.Property(
                "attributes",
                th.ArrayType(
                    th.ObjectType(
                        th.Property("name", th.StringType),
                        th.Property("value", th.StringType),
                    )
                ),
            ),
        ),
    ),
    th.Property(
        "answers",
        th.ArrayType(
            th.ObjectType(
                th.Property("question_id", th.IntegerType),
                th.Property("question_type", th.StringType),
                th.Property(
                    "answer",
                    th.CustomType({
                        "anyOf": [
                            {"type": "string"},
                            {
                                "type": "object",
                                "properties": {
                                    "id": {"type": ["integer", "null"]},
                                    "content": {"type": ["string", "null"]},
                                    "comment": {"type": ["string", "null"]},
                                    "translated_comment": {"type": ["string", "null"]},
                                    "disclaimer_accepted": {"type": ["boolean", "null"]},
                                    "rating": {"type": ["integer", "null"]},
                                    "tag": {"type": ["string", "null"]},
                                },
                            },
                            {"type": "null"},
                        ]
                    }),
                ),
            )
        ),
    ),
).to_dict()


def build_survey_responses_stream(survey_id: str) -> type[SurvicateStream]:
    """Return a responses stream class bound to a single survey."""
    _survey_id = survey_id

    def _get_new_paginator(_self: SurvicateStream) -> SurvivatePaginator:
        return SurvivatePaginator()

    def _post_process(
        _self: SurvicateStream,
        row: dict,
        _context: Context | None = None,
    ) -> dict | None:
        row["survey_id"] = _survey_id
        return row

    return type(
        "SurveyResponsesStream",
        (SurvicateStream,),
        {
            "name": f"survey_responses_{survey_id}",
            "path": f"/surveys/{survey_id}/responses",
            "primary_keys": ("uuid",),
            "replication_key": "collected_at",
            "schema": _RESPONSES_SCHEMA,
            "get_new_paginator": _get_new_paginator,
            "post_process": _post_process,
        },
    )
