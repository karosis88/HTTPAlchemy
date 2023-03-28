
_HttpAlchemy_ is a Python library that provides a [curl](https://github.com/curl/curl) interface for interacting with Python HTTP client libraries like requests.

# Install
``` shell
$ pip install httpalchemy
```

# Quick Start

``` python
>>> from httpalchemy import curl
>>> response = curl("http://google.com")
>>> response
<CurlResponse [301 Moved Permanently]>
>>> decoded_body = response.text
>>> raw_body = response.content
>>> response.encoding
'UTF-8'
>>> response.raw  # get raw response, `requests` library response by default
<Response [301]>
```

## How to predict `HTTPAlchemy` syntax

HTTPAlchemy uses the [curl](https://github.com/curl/curl) syntax.

There are several rules to follow.
    
* Options such as "-X" are converted to "_X"
* Options such as "--header" are converted to "__header"

## Examples

``` python 
curl http://example.com -d "test_data"  # curl
curl("http://example.com", _d="test_data")  # HTTPAlchemy
```

``` python 
curl http://example.com -d "{'test': 'test'}" -H 'Content-Type: application/json'  # curl
curl("http://example.com", _d="test_data", _H=["Content-Type: application/json"])  # HTTPAlchemy
```

``` shell
curl ... -H "header1: value1" -H "header2: value2"
curl(..., _H=[("header1", "value1"), ("header2", "value2")])
```

HTTPAlchemy can accept headers in one of the following formats.
``` python
curl(_H={"header1": "value1", "header2": "value2"})
curl(_H=[("header1", "value1"), ("header2", "value2")])
curl(_H=["header1: value1", "header2: value2"])
```

## Proxies

HTTPAlchemy provides proxy support via the `http_proxy` and `https_proxy` environment variables.

``` shell
$ export http_proxy="http://example.com"
$ export https_proxy="https://example.com"
$ python script.py
```