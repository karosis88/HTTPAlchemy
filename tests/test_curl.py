import pytest

from src._curl import create_curl_request
from src._curl import curl
from src._curl import normalize_auth
from src._curl import normalize_forms
from src._curl import normalize_header_and_form
from src._curl import normalize_headers
from src._exceptions import IncompatibleTypeError
from src._exceptions import RepeatedAliasesError


def test_repeated_options():
    with pytest.raises(RepeatedAliasesError):
        curl("example.com", _d="test_data", __data="test_data1")


def test_headers_normalizing():
    # Passing already normalized header
    headers = normalize_headers({"Content-Type": "application/json"})
    assert headers == {"Content-Type": "application/json"}

    # Passing headers type of `typing.Iterable[typing.Tuple[str, str]]`
    headers = normalize_headers([("Content-Type", "application/json")])
    assert headers == {"Content-Type": "application/json"}

    # Passing headers type of `typing.Iterable[typing.Tuple[str, str]]`
    # It's a curl interface
    headers = normalize_headers(["Content-Type: application/json"])
    assert headers == {"Content-Type": "application/json"}


def test_forms_normalizing():
    # Passing already normalized header
    forms = normalize_forms({"file1": "test.jpg"})
    assert forms == {"file1": "test.jpg"}

    # Passing headers type of `typing.Iterable[typing.Tuple[str, str]]`
    forms = normalize_forms([("file1", "test.jpg")])
    assert forms == {"file1": "test.jpg"}

    # Passing headers type of `typing.Iterable[typing.Tuple[str, str]]`
    # It's a curl interface
    forms = normalize_forms(["file1=test.jpg"])
    assert forms == {"file1": "test.jpg"}


def test_auth_normalizing():
    # Passing already normalized auth
    auth = normalize_auth(("login", "pass"))
    assert auth == ("login", "pass")

    # Passing auth type of `str`
    auth = normalize_auth("login:pass")
    assert auth == ("login", "pass")


def test_forms_and_headers_normalizing_type_errors():
    with pytest.raises(IncompatibleTypeError):
        normalize_header_and_form({"invalid type": 2}, seperator=...)

    with pytest.raises(IncompatibleTypeError):
        normalize_header_and_form(5, seperator=...)

    with pytest.raises(IncompatibleTypeError):
        normalize_header_and_form([("Content-Type", 5)], seperator=...)


def test_curl_request_generating():
    curl_request = create_curl_request("http://google.com")
    assert curl_request.url == "http://google.com"

    curl_request = create_curl_request(
        "http://example.com", _X="POST", _H=[("Content-Type", "text/json")]
    )
    assert curl_request.method == "POST"
    assert curl_request.headers == {"Content-Type": "text/json"}

    curl_request = create_curl_request(
        "https://example.com", _X="POST", _d="key1=val1&key2=val2"
    )
    assert curl_request.data == "key1=val1&key2=val2"
    assert curl_request.method == "POST"

    curl_request = create_curl_request(
        "https://example.com", _L=True, _v=True, _F=[("key1", "val1")]
    )
    assert curl_request.follow_redirects
    assert curl_request.verbose
    assert curl_request.form == {"key1": "val1"}
