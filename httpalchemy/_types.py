import typing

CREDENTIALS = typing.Union[str, typing.Tuple[str, str]]
FORM_DATA = typing.Union[
    typing.Iterable[typing.Union[str, typing.Tuple[str, str], typing.Dict[str, str]]]
]
HEADERS = typing.Union[
    typing.Iterable[typing.Union[str, typing.Tuple[str, str]]], typing.Dict[str, str]
]
METHOD = typing.Literal[
    "GET", "POST", "PUT", "DELETE", "PATCH", "CONNECT", "LINK", "UNLINK"
]
