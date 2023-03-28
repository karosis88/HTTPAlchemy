import io
import typing
from abc import ABC
from abc import abstractmethod
from enum import Enum
from enum import auto
from . import config

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
    def _convert_request(self, curl_request: "CurlRequest") -> typing.Tuple[REQUESTS, typing.Dict[str, str]]:
        ...

    @abstractmethod
    def _send(
            self, request: "RequestsRequest", curl_request: "CurlRequest", proxies: typing.Dict[str, str]
    ) -> "RequestsResponse":
        ...

    @abstractmethod
    def handle_curl(self, request: "CurlRequest") -> "CurlResponse":
        ...


class requestsEngine(Engine):
    DEFAULT_HEADERS = {
        "Accept": "*/*",
    }

    def _convert_request(self, curl_request: "CurlRequest") -> typing.Tuple["RequestsRequest", typing.Dict[str, str]]:
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

        proxies = {}
        if config.HTTPS_PROXY:
            proxies['https'] = config.HTTPS_PROXY
        if config.HTTP_PROXY:
            proxies['http'] = config.HTTP_PROXY

        for key, value in form.items():
            if value[0] == "@":
                filename = value[1:]
                cleaned_form[key] = (filename, open(filename, "rb"))

        headers["User-Agent"] = user_agent or DEFAULT_USER_AGENT

        merged_headers = self.DEFAULT_HEADERS
        merged_headers.update(headers)

        req = Request(
            url=url,
            method=method,
            data=data,
            files=cleaned_form,
            headers=merged_headers,
        )
        return req, proxies

    def _send(
            self, request: "RequestsRequest", curl_request: "CurlRequest", proxies: typing.Dict[str, str]
    ) -> "RequestsResponse":

        with requests.Session() as s:
            response = s.send(
                request.prepare(),
                allow_redirects=curl_request.follow_redirects,
                proxies=proxies
            )

        return response

    def handle_curl(self, request: "CurlRequest") -> "CurlResponse":
        from ._curl import CurlResponse

        requests_request, proxies = self._convert_request(curl_request=request)
        response = self._send(request=requests_request, curl_request=request, proxies=proxies)
        return CurlResponse(
            status_code=response.status_code,
            reason=response.reason,
            raw_response=response,
            request=request,
        )


class engines(Enum):
    requests: typing.Type[Engine] = requestsEngine


ENGINE_LITERALS = typing.Literal["requests"]
