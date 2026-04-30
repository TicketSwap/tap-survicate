"""JSON schema definitions for tap-survicate streams."""

from __future__ import annotations

from singer_sdk import typing as th

SURVEYS_SCHEMA = th.PropertiesList(
    th.Property("id", th.StringType, required=True),
    th.Property("type", th.StringType),
    th.Property("name", th.StringType),
    th.Property("created_at", th.DateTimeType),
    th.Property("enabled", th.BooleanType),
    th.Property("responses", th.IntegerType),
    th.Property(
        "launch",
        th.ObjectType(
            th.Property("start_at", th.DateTimeType),
            th.Property("end_at", th.DateTimeType),
            th.Property("responses_limit", th.IntegerType),
        ),
    ),
    th.Property(
        "author",
        th.ObjectType(
            th.Property("name", th.StringType),
            th.Property("email", th.StringType),
        ),
    ),
    th.Property("folder", th.StringType),
    th.Property("first_response_at", th.DateTimeType),
    th.Property("last_response_at", th.DateTimeType),
    th.Property("attributes", th.ArrayType(th.StringType)),
).to_dict()

QUESTIONS_SCHEMA = th.PropertiesList(
    th.Property("id", th.IntegerType, required=True),
    th.Property("survey_id", th.StringType),
    th.Property("type", th.StringType),
    th.Property("name", th.StringType),
    th.Property("position", th.IntegerType),
    th.Property("required", th.BooleanType),
    th.Property(
        "answers",
        th.ArrayType(
            th.ObjectType(
                th.Property("id", th.IntegerType),
                th.Property("name", th.StringType),
                th.Property("position", th.IntegerType),
            )
        ),
    ),
).to_dict()

RESPONSES_SCHEMA = th.PropertiesList(
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

_ANSWER_TYPE = th.CustomType({
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
})

QUESTION_RESPONSES_SCHEMA = th.PropertiesList(
    th.Property("response_uuid", th.StringType, required=True),
    th.Property("survey_id", th.StringType),
    th.Property("question_id", th.IntegerType, required=True),
    th.Property("question_type", th.StringType),
    th.Property("answer", _ANSWER_TYPE),
).to_dict()
