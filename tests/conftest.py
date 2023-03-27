import pytest


@pytest.fixture
def SERVER_URL():
    return "http://127.0.0.1:7575"


@pytest.fixture
def ECHO_BODY_URL(SERVER_URL):
    return SERVER_URL + "/echo_body"


@pytest.fixture
def FILE_UPLOAD_URL(SERVER_URL):
    return SERVER_URL + "/file_upload"


@pytest.fixture
def FILES_UPLOAD_URL(SERVER_URL):
    return SERVER_URL + "/files_upload"


@pytest.fixture
def ECHO_HEADERS(SERVER_URL):
    return SERVER_URL + "/echo_headers"


@pytest.fixture
def JSON_URL(SERVER_URL):
    return SERVER_URL + "/json_url"
