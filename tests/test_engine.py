from tempfile import NamedTemporaryFile

from src._curl import curl


def test_requests_simple_request(SERVER_URL):
    resp = curl(SERVER_URL)
    assert resp.status_code == 200


def test_requests_body_sending(ECHO_BODY_URL):
    resp = curl(ECHO_BODY_URL, _X="POST", _d="key=value")
    assert resp.status_code == 200
    assert resp.raw.text == '"key=value"'

    assert "Content-Type" in resp.raw.request.headers
    assert (
        resp.raw.request.headers["Content-Type"] == "application/x-www-form-urlencoded"
    )

    resp = curl(ECHO_BODY_URL, _X="POST")
    assert resp.raw.text == '""'


def test_requests_multipart_sending(FILE_UPLOAD_URL):
    with NamedTemporaryFile(mode="wb+", buffering=0) as f:
        f.write(b"test-data")
        resp = curl(FILE_UPLOAD_URL, _F=[f"file=@{f.name}"], _X="POST")
        assert resp.status_code == 200
        assert resp.text() == "9"  # length of the data which was sent


def test_requests_multipart_sending_multiple_files(FILES_UPLOAD_URL):
    with NamedTemporaryFile(mode="wb+", buffering=0) as f, NamedTemporaryFile(
        mode="wb+", buffering=0
    ) as f1:
        f.write(b"test-data")
        f1.write(b"test_data1")
        resp = curl(
            FILES_UPLOAD_URL, _F=[f"file=@{f.name}", f"file1=@{f1.name}"], _X="POST"
        )
        assert resp.status_code == 200
        assert resp.text() == "19"  # length of the data which was sent


def test_requests_headers_building(ECHO_HEADERS):
    resp = curl(ECHO_HEADERS, _A="My-Agent")
    assert resp.json()["user-agent"] == "My-Agent"


def test_requests_json_request(JSON_URL):
    resp = curl(
        JSON_URL, _H=[("Content-Type", "application/json")], _d='{"test": "test"}'
    )
    assert resp.ok()
    assert resp.json() == {"test": "test"}
