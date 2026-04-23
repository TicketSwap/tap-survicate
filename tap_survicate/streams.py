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
    """Surveys — used as a parent stream to iterate responses per survey."""

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
        survey_names: list[str] | None = self.config.get("survey_names")
        if survey_names is not None and row.get("name") not in survey_names:
            return None
        return row

    @override
    def get_child_context(self, record: dict, context: Context | None) -> dict:
        """Pass survey_id to child streams."""
        return {"survey_id": record["id"]}


class ResponsesStream(SurvicateStream):
    """All responses collected for each survey."""

    name = "responses"
    path = "/surveys/{survey_id}/responses"
    primary_keys = ("uuid",)
    replication_key = "collected_at"
    parent_stream_type = SurveysStream

    @override
    def get_new_paginator(self) -> SurvivatePaginator:
        return SurvivatePaginator()

    schema = th.PropertiesList(
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