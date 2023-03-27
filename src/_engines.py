import io
import typing
from abc import ABC
from abc import abstractmethod
from enum import Enum

import requests

from .config import DEFAULT_USER_AGENT

try:
    from requests import Request as RequestsRequest
    from requests import Response as RequestsResponse
except Exception:
    ...
try:
    from httpx import Request as HttpxRequest
    from httpx import Response as HttpxResponse
except Exception:
    ...

if typing.TYPE_CHECKING:
    from ._curl import CurlRequest
    from ._curl import CurlResponse

ENGINE_LITERAL = typing.Literal["requests", "httpx"]
REQUESTS = typing.Union["RequestsRequest", "HttpxRequest"]
RESPONSES = typing.Union["HttpxResponse", "RequestsResponse"]


class Engine(ABC):
    @abstractmethod
    def _convert_request(self, curl_request: "CurlRequest") -> REQUESTS:
        ...

    @abstractmethod
    def _send(
        self, request: "RequestsRequest", curl_request: "CurlRequest"
    ) -> "RequestsResponse":
        ...

    @abstractmethod
    def handle_curl(self, request: "CurlRequest") -> "CurlResponse":
        ...


class requestsEngine(Engine):
    DEFAULT_HEADERS = {
        "Accept": "*/*",
    }

    def _convert_request(self, curl_request: "CurlRequest") -> "RequestsRequest":
        from requests import Request

        url = curl_request.url
        method = curl_request.method
        data = curl_request.data
        headers = curl_request.headers
        form = curl_request.form
        user_agent = curl_request.user_agent
        cleaned_form: typing.Dict[
            str, typing.Union[str, typing.Tuple[str, io.BufferedReader]]
        ] = {}

        if headers is None:
            headers = {}
        if data is not None and "Content-Type" not in headers:
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        if form is None:
            form = {}

        for key, value in form.items():
            if value[0] == "@":
                filename = value[1:]
                cleaned_form[key] = (filename, open(filename, "rb"))

        headers.update(self.DEFAULT_HEADERS)
        headers["User-Agent"] = user_agent or DEFAULT_USER_AGENT

        req = Request(
            url=url,
            method=method,
            data=data,
            files=cleaned_form,
            headers=headers,
        )
        return req

    def _send(
        self, request: "RequestsRequest", curl_request: "CurlRequest"
    ) -> "RequestsResponse":
        with requests.Session() as s:
            response = s.send(
                request.prepare(), allow_redirects=curl_request.follow_redirects
            )
        return response

    def handle_curl(self, request: "CurlRequest") -> "CurlResponse":
        from ._curl import CurlResponse

        requests_request = self._convert_request(curl_request=request)
        response = self._send(request=requests_request, curl_request=request)
        return CurlResponse(
            status_code=response.status_code,
            reason=response.reason,
            raw_response=response,
            request=request,
        )


class engines(Enum):
    requests: typing.Type[Engine] = requestsEngine


ENGINE_LITERALS = typing.Literal["requests"]
