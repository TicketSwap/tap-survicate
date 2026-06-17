"""Stream type classes for tap-survicate."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from urllib.parse import ParseResult, parse_qsl

from tap_survicate.client import SurvicateStream
from tap_survicate.schemas import (
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


class SurveyResponsesStream(SurvicateStream):
    """Responses for a survey — child of SurveysStream."""

    name = "survey_responses"
    parent_stream_type = SurveysStream
    path = "/surveys/{id}/responses"
    primary_keys = ("uuid",)
    replication_key = "collected_at"
    schema = RESPONSES_SCHEMA

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: ParseResult | None,
    ) -> dict:
        if next_page_token:
            # HATEOAS paginator passes a ParseResult; forward its query params verbatim
            return dict(parse_qsl(next_page_token.query))
        if context and context.get("attributes") is not None:
            return {"attributes[]": context["attributes"]}
        return {}

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        row["survey_id"] = context.get("id") if context else None
        return row
