"""REST client handling, including SurvicateStream base class."""

from __future__ import annotations

import sys
import urllib.parse
from typing import Any

import requests
from singer_sdk.authenticators import APIKeyAuthenticator
from singer_sdk.pagination import BaseHATEOASPaginator
from singer_sdk.streams import RESTStream

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class SurvivatePaginator(BaseHATEOASPaginator):
    """Stops when the response data array is empty, even if next_url is present."""

    def get_next_url(self, response: requests.Response) -> str | None:
        body: dict[str, Any] = response.json()
        if not body.get("data"):
            return None
        next_url = body.get("pagination_data", {}).get("next_url")
        # The SDK parses URLs into ParseResult before loop detection, so compare the
        # same way to bail out early instead of letting the SDK raise RuntimeError.
        if next_url and urllib.parse.urlparse(next_url) == self.current_value:
            return None
        return next_url


class SurvicateStream(RESTStream):
    """Survicate stream class."""

    records_jsonpath = "$.data[*]"
    next_page_token_jsonpath = "$.pagination_data.next_url"

    @override
    @property
    def url_base(self) -> str:
        """Return the API URL root."""
        return "https://data-api.survicate.com/v2"

    @override
    def get_new_paginator(self) -> SurvivatePaginator:
        return SurvivatePaginator()

    @override
    @property
    def authenticator(self) -> APIKeyAuthenticator:
        """Return authenticator with Basic auth header."""
        return APIKeyAuthenticator(
            stream=self,
            key="Authorization",
            value=f"Basic {self.config['api_key']}",
            location="header",
        )
