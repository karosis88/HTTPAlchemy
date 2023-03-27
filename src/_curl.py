import re
import typing

from ._engines import ENGINE_LITERAL
from ._engines import RESPONSES
from ._engines import Engine
from ._engines import engines
from ._exceptions import IncompatibleTypeError
from ._exceptions import RepeatedAliasesError
from ._types import CREDENTIALS
from ._types import FORM_DATA
from ._types import HEADERS
from ._types import METHOD

OPTIONS = [
    ("_d", "__data"),
    ("_F", "__form"),
    ("_u", "__user"),
    ("_A", "__user_agent"),
    ("_v", "__verbose"),
    ("_H", "__header"),
    ("_L", "__location"),
    ("_X", "__request"),
]


class CurlRequest:
    def __init__(
        self,
        url: str,
        /,
        *,
        data: typing.Optional[str],
        form: typing.Optional[typing.Dict[str, str]],
        auth: typing.Optional[typing.Tuple[str, str]],
        user_agent: typing.Optional[str],
        verbose: typing.Optional[bool],
        headers: typing.Optional[typing.Dict[str, str]],
        method: typing.Optional[METHOD],
        follow_redirects: bool = False,
    ):
        self.url = url
        self.data = data
        self.form = form
        self.auth = auth
        self.user_agent = user_agent
        self.verbose = verbose
        self.headers = headers
        self.follow_redirects = follow_redirects
        self.method = method


class CurlResponse:
    def __init__(
        self,
        status_code: int,
        reason: str,
        raw_response: RESPONSES,
        request: CurlRequest,
    ):
        self.status_code = status_code
        self.reason = reason
        self.raw = raw_response
        self.request = request

    def ok(self) -> bool:
        return self.status_code // 100 == 2

    def text(self) -> str:
        return self.raw.text

    def json(self) -> str:
        return self.raw.json()

    def __repr__(self):
        return "<CurlResponse [%d %s]>" % self.status_code, self.reason


def normalize_header_and_form(
    header_or_form: typing.Union[HEADERS, FORM_DATA], seperator: str
) -> typing.Dict[str, str]:
    if isinstance(header_or_form, dict):
        for header, header_value in header_or_form.items():
            for value in (header, header_value):
                if not isinstance(value, str):
                    msg = (
                        "Expected a string instance but received an instance "
                        "of `%s` (%r)"
                    ) % (value.__class__.__name__, value)
                    raise IncompatibleTypeError(msg)
        return header_or_form
    try:
        iterator = iter(header_or_form)
    except TypeError:
        msg = (
            "Value must be either a dictionary or an iterable object, not `%s`"
            % header_or_form.__class__.__name__
        )
        raise IncompatibleTypeError(msg)

    final_dict: typing.Dict[str, str] = {}

    for single_header_or_form in iterator:
        if isinstance(single_header_or_form, str):
            key, value = single_header_or_form.split(seperator)
            final_dict[key] = value
        elif isinstance(single_header_or_form, tuple):
            key, value = single_header_or_form
            final_dict[key] = value
        else:
            msg = (
                "The iterable object must be of the type `Tuple[str, str]` "
                "or `str` not `%s`"
            ) % single_header_or_form.__class__.__name__
            raise IncompatibleTypeError(msg)
        for val in (key, value):
            if not isinstance(val, str):
                msg = (
                    "The key and value in the header "
                    "must be instances of `str` not `%s`" % val.__class__.__name__
                )
                raise IncompatibleTypeError(msg)
    return final_dict


def normalize_headers(headers: HEADERS) -> typing.Dict[str, str]:
    """Convert any header-compatible type to `typing.Dict[str, str]` type"""
    return normalize_header_and_form(header_or_form=headers, seperator=": ")


def normalize_forms(forms: FORM_DATA) -> typing.Dict[str, str]:
    """Convert any form-data-compatible type to `typing.Dict[str, str]` type"""
    return normalize_header_and_form(header_or_form=forms, seperator="=")


def normalize_auth(auth: CREDENTIALS) -> typing.Tuple[str, str]:
    """Convert any auth-compatible type to `typing.Tuple[str, str]` type"""

    if isinstance(auth, tuple):
        if len(auth) != 2:
            msg = (
                "Credentials must be a pair of login and password, but "
                "there are credentials with length of %d"
            ) % len(auth)
            raise IncompatibleTypeError(msg)

        for credential in auth:
            if not isinstance(credential, str):
                msg = (
                    "Credential must be a `str` instance, but got `%s`"
                    % credential.__class__.__name__
                )
                raise IncompatibleTypeError(msg)
        return auth

    elif isinstance(auth, str):
        match = re.match("(.*):(.*)", auth)
        if not match:
            msg = "Credential is invalid, expected `LOGIN + ':' + 'PASSWORD'`"
            raise IncompatibleTypeError(msg)
        return match.group(1), match.group(2)
    else:
        msg = (
            "Credential must be either a `Tuple[str, str]` or `str` but got `%s`"
            % auth.__class__.__name__
        )
        raise IncompatibleTypeError(msg)


def create_curl_request(
    url: str,
    /,
    *,
    _d: typing.Optional[str] = None,
    __data: typing.Optional[str] = None,
    _F: typing.Optional[FORM_DATA] = None,
    __form: typing.Optional[FORM_DATA] = None,
    _u: typing.Optional[CREDENTIALS] = None,
    __user: typing.Optional[CREDENTIALS] = None,
    _A: typing.Optional[str] = None,
    __user_agent: typing.Optional[str] = None,
    _v: typing.Optional[bool] = None,
    __verbose: typing.Optional[bool] = None,
    _H: typing.Optional[HEADERS] = None,
    __header: typing.Optional[HEADERS] = None,
    _L: typing.Optional[bool] = None,
    __location: typing.Optional[bool] = None,
    _X: METHOD = "GET",
    __request: typing.Optional[METHOD] = None,
) -> CurlRequest:
    headers = normalize_headers(headers=_H) if _H else None
    forms = normalize_forms(forms=_F) if _F else None
    auth = normalize_auth(_u) if _u else None
    data = _d
    user_agent = _A
    verbose = bool(_v)
    follow_redirects = bool(_L)
    method = _X

    curl_request: CurlRequest = CurlRequest(
        url,
        data=data,
        form=forms,
        auth=auth,
        user_agent=user_agent,
        verbose=verbose,
        follow_redirects=follow_redirects,
        headers=headers,
        method=method,
    )

    return curl_request


def curl(
    url: str,
    /,
    *,
    _d: typing.Optional[str] = None,
    __data: typing.Optional[str] = None,
    _F: typing.Optional[FORM_DATA] = None,
    __form: typing.Optional[FORM_DATA] = None,
    _u: typing.Optional[CREDENTIALS] = None,
    __user: typing.Optional[CREDENTIALS] = None,
    _A: typing.Optional[str] = None,
    __user_agent: typing.Optional[str] = None,
    _v: typing.Optional[bool] = None,
    __verbose: typing.Optional[bool] = None,
    _H: typing.Optional[HEADERS] = None,
    __header: typing.Optional[HEADERS] = None,
    _L: typing.Optional[bool] = None,
    __location: typing.Optional[bool] = None,
    _X: METHOD = "GET",
    __request: typing.Optional[METHOD] = None,
    engine: typing.Union[engines, ENGINE_LITERAL] = engines.requests,
) -> CurlResponse:
    for option, option_alias in OPTIONS:
        if locals()[option] is not None and locals()[option_alias] is not None:
            msg = (
                "Because options '%s' and '%s' are "
                "aliases, only one of them can be used." % (option, option_alias)
            )
            raise RepeatedAliasesError(msg)
        locals()[option] = locals()[option] or locals()[option_alias]

    curl_request = create_curl_request(
        url,
        _d=_d,
        _F=_F,
        _u=_u,
        _A=_A,
        _v=_v,
        _H=_H,
        _L=_L,
        _X=_X,
    )
    if isinstance(engine, str):
        engine_enum = getattr(engines, engine)
    else:
        engine_enum = engine
    engine_class = typing.cast(Engine, engine_enum.value())
    response = engine_class.handle_curl(curl_request)
    return response
