from __future__ import absolute_import, division, print_function

import functools
import hmac
import io
import logging
import sys
import os
import re
import time
import threading

import fintecture
from fintecture import six
from fintecture.six.moves.urllib.parse import parse_qsl, quote_plus

FINTECTURE_LOG = os.environ.get("FINTECTURE_LOG")

logger = logging.getLogger("fintecture")

__all__ = [
    "io",
    "parse_qsl",
    "utf8",
    "log_info",
    "log_debug",
    "logfmt",
]


def utf8(value):
    if six.PY2 and isinstance(value, six.text_type):
        return value.encode("utf-8")
    else:
        return value


def is_appengine_dev():
    return "APPENGINE_RUNTIME" in os.environ and "Dev" in os.environ.get(
        "SERVER_SOFTWARE", ""
    )


def _console_log_level():
    if fintecture.log in ["debug", "info"]:
        return fintecture.log
    elif FINTECTURE_LOG in ["debug", "info"]:
        return FINTECTURE_LOG
    else:
        return None


def log_debug(message, **params):
    msg = logfmt(dict(message=message, **params))
    if _console_log_level() == "debug":
        print(msg, file=sys.stderr)
    logger.debug(msg)


def log_info(message, **params):
    msg = logfmt(dict(message=message, **params))
    if _console_log_level() in ["debug", "info"]:
        print(msg, file=sys.stderr)
    logger.info(msg)


def logfmt(props):
    def fmt(key, val):
        # Handle case where val is a bytes or bytesarray
        if six.PY3 and hasattr(val, "decode"):
            val = val.decode("utf-8")
        # Check if val is already a string to avoid re-encoding into
        # ascii. Since the code is sent through 2to3, we can't just
        # use unicode(val, encoding='utf8') since it will be
        # translated incorrectly.
        if not isinstance(val, six.string_types):
            val = six.text_type(val)
        if re.search(r"\s", val):
            val = repr(val)
        # key should already be a string
        if re.search(r"\s", key):
            key = repr(key)
        return u"{key}={val}".format(key=key, val=val)

    return u" ".join([fmt(key, val) for key, val in sorted(props.items())])


# Borrowed from Django's source code
if hasattr(hmac, "compare_digest"):
    # Prefer the stdlib implementation, when available.
    def secure_compare(val1, val2):
        return hmac.compare_digest(utf8(val1), utf8(val2))

else:

    def secure_compare(val1, val2):
        """
        Returns True if the two strings are equal, False otherwise.
        The time taken is independent of the number of characters that match.
        For the sake of simplicity, this function executes in constant time
        only when the two strings have the same length. It short-circuits when
        they have different lengths.
        """
        val1, val2 = utf8(val1), utf8(val2)
        if len(val1) != len(val2):
            return False
        result = 0
        if six.PY3 and isinstance(val1, bytes) and isinstance(val2, bytes):
            for x, y in zip(val1, val2):
                result |= x ^ y
        else:
            for x, y in zip(val1, val2):
                result |= ord(x) ^ ord(y)
        return result == 0


def get_object_classes():
    # This is here to avoid a circular dependency
    from fintecture.object_classes import OBJECT_CLASSES

    return OBJECT_CLASSES


def convert_to_fintecture_object(
    resp, app_id=None, fintecture_version=None, params=None
):
    # If we get a FintectureResponse, we'll want to return a
    # FintectureObject with the last_response field filled out with
    # the raw API response information
    fintecture_response = None

    if isinstance(resp, fintecture.fintecture_response.FintectureResponse):
        fintecture_response = resp
        resp = fintecture_response.data

    if isinstance(resp, list):
        return [
            convert_to_fintecture_object(
                i, app_id, fintecture_version
            )
            for i in resp
        ]
    elif isinstance(resp, dict) and not isinstance(
        resp, fintecture.fintecture_object.FintectureObject
    ):
        resp = resp.copy()
        klass_name = resp.get("object")
        if isinstance(klass_name, six.string_types):
            klass = get_object_classes().get(
                klass_name, fintecture.fintecture_object.FintectureObject
            )
        else:
            klass = fintecture.fintecture_object.FintectureObject

        obj = klass.construct_from(
            resp,
            app_id,
            fintecture_version=fintecture_version,
            last_response=fintecture_response,
        )

        # We only need to update _retrieve_params when special params were
        # actually passed. Otherwise, leave it as is as the list / search result
        # constructors will instantiate their own params.
        if (
            params is not None
            and hasattr(obj, "object")
            and ((obj.object == "list") or (obj.object == "search_result"))
        ):
            obj._retrieve_params = params

        return obj
    else:
        return resp


def convert_to_dict(obj):
    """Converts a FintectureObject back to a regular dict.

    Nested FintectureObjects are also converted back to regular dicts.

    :param obj: The FintectureObject to convert.

    :returns: The FintectureObject as a dict.
    """
    if isinstance(obj, list):
        return [convert_to_dict(i) for i in obj]
    # This works by virtue of the fact that FintectureObjects _are_ dicts. The dict
    # comprehension returns a regular dict and recursively applies the
    # conversion to each value.
    elif isinstance(obj, dict):
        return {k: convert_to_dict(v) for k, v in six.iteritems(obj)}
    else:
        return obj


def read_special_variable(params, key_name, default_value):
    value = default_value
    params_value = None

    if params is not None and key_name in params:
        params_value = params[key_name]
        del params[key_name]

    if value is None:
        value = params_value

    return value


def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


def sanitize_id(id):
    utf8id = utf8(id)
    quotedId = quote_plus(utf8id)
    return quotedId


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


class Interval:
    def __init__(self, interval, action):
        self.interval = interval
        self.action = action
        self.stopEvent = threading.Event()
        thread = threading.Thread(target=self._set_interval)
        thread.start()

    def _set_interval(self):
        next_time = time.time() + self.interval
        while not self.stopEvent.wait(next_time-time.time()):
            next_time += self.interval
            self.action()

    def cancel(self) :
        self.stopEvent.set()


class class_method_variant(object):

    def __init__(self, class_method_name):
        self.class_method_name = class_method_name

    def __call__(self, method):
        self.method = method
        return self

    def __get__(self, obj, objtype=None):
        @functools.wraps(self.method)
        def _wrapper(*args, **kwargs):
            if obj is not None:
                # Method was called as an instance method, e.g.
                # instance.method(...)
                return self.method(obj, *args, **kwargs)
            elif len(args) > 0 and isinstance(args[0], objtype):
                # Method was called as a class method with the instance as the
                # first argument, e.g. Class.method(instance, ...) which in
                # Python is the same thing as calling an instance method
                return self.method(args[0], *args[1:], **kwargs)
            else:
                # Method was called as a class method, e.g. Class.method(...)
                class_method = getattr(objtype, self.class_method_name)
                return class_method(*args, **kwargs)

        return _wrapper
