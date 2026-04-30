"""Stream type classes for tap-survicate."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tap_survicate.client import SurvicateStream
from tap_survicate.schemas import (
    QUESTION_RESPONSES_SCHEMA,
    QUESTIONS_SCHEMA,
    RESPONSES_SCHEMA,
    SURVEYS_SCHEMA,
)

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Iterable

    import requests
    from singer_sdk.helpers.types import Context


class SurveysStream(SurvicateStream):
    """Surveys metadata stream."""

    name = "surveys"
    path = "/surveys"
    primary_keys = ("id",)
    replication_key = None
    schema = SURVEYS_SCHEMA

    @override
    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        for record in super().parse_response(response):
            survey_id = record["id"]
            detail_url = f"{self.url_base}/surveys/{survey_id}"
            detail_resp = self.requests_session.get(
                detail_url,
                headers={"Authorization": f"Basic {self.config['api_key']}"},
                timeout=30,
            )
            detail_resp.raise_for_status()
            yield detail_resp.json()

    @override
    def get_child_context(self, record: dict, context: Context | None = None) -> dict:
        return {"id": record["id"], "attributes": record.get("attributes") or []}

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        survey_ids: list[str] | None = self.config.get("survey_ids")
        if survey_ids is not None and row.get("id") not in survey_ids:
            return None
        return row


class SurveyQuestionsStream(SurvicateStream):
    """Questions for a survey — child of SurveysStream."""

    name = "survey_questions"
    parent_stream_type = SurveysStream
    path = "/surveys/{id}/questions"
    primary_keys = ("id", "survey_id")
    replication_key = None
    schema = QUESTIONS_SCHEMA

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        row["survey_id"] = context.get("id")
        return row


class SurveyResponsesStream(SurvicateStream):
    """Responses for a survey — child of SurveysStream."""

    name = "survey_responses"
    parent_stream_type = SurveysStream
    path = "/surveys/{id}/responses"
    primary_keys = ("uuid",)
    replication_key = "collected_at"
    schema = RESPONSES_SCHEMA

    @override
    def _request(
        self,
        prepared_request: requests.PreparedRequest,
        context: Context | None,
    ) -> requests.Response:
        if prepared_request.url:
            prepared_request.url = prepared_request.url.replace("%2C", ",")
        self.logger.info("SurveyResponsesStream request URL: %s", prepared_request.url)
        return super()._request(prepared_request, context)

    @override
    def get_url_params(
        self,
        context: Context | None,
        _next_page_token: str | None,
    ) -> dict:
        if context.get("attributes") is not None:
            return {"attributes[]": context["attributes"]}
        return {}

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        row["survey_id"] = context.get("id")
        return row

    @override
    def get_child_context(self, record: dict, context: Context | None = None) -> dict:
        return {
            "survey_id": record["survey_id"],
            "response_uuid": record["uuid"],
            "answers": record.get("answers") or [],
        }


class SurveyQuestionResponsesStream(SurvicateStream):
    """Individual question answers — child of SurveyResponsesStream."""

    name = "survey_question_responses"
    parent_stream_type = SurveyResponsesStream
    path = ""
    primary_keys = ("response_uuid", "question_id")
    replication_key = None
    schema = QUESTION_RESPONSES_SCHEMA

    @override
    def get_records(self, context: Context | None) -> Iterable[dict]:
        for answer in (context or {}).get("answers", []):
            yield {
                "survey_id": context["survey_id"],
                "response_uuid": context["response_uuid"],
                **answer,
            }
