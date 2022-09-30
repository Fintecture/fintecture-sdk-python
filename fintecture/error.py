from __future__ import absolute_import, division, print_function

import json

import fintecture
from fintecture.six import python_2_unicode_compatible


@python_2_unicode_compatible
class FintectureError(Exception):
    def __init__(
        self,
        message=None,
        url=None,
        http_body=None,
        http_status=None,
        json_body=None,
        headers=None,
        code=None,
    ):
        super(FintectureError, self).__init__(message)

        if http_body and hasattr(http_body, "decode"):
            try:
                http_body = http_body.decode("utf-8")
            except BaseException:
                http_body = (
                    "<Could not decode body as utf-8. "
                    "Please report to contact@fintecture.com>"
                )

            if not json_body:
                try:
                    json_body = json.loads(http_body, object_pairs_hook=OrderedDict)
                except Exception:
                    http_body = (
                        "<Could not parse http body as a JSON format. "
                        "Please report to contact@fintecture.com>"
                    )

        self._message = message
        self.url = url
        self.http_body = http_body
        self.http_status = http_status
        self.json_body = json_body
        self.log_id = json_body.get('log_id', None) if json_body else None
        self.errors = json_body.get('errors', None) if json_body else None
        self.headers = headers or {}
        self.code = code
        self.x_request_id = self.headers.get("x-request-id", None)
        self.error = self.construct_error_object()

    def __str__(self):
        msg = self._message or "<empty message>"
        if self.x_request_id is not None:
            if self.log_id is not None:
                return u"Request {0} - Log ID {1}: {2}".format(self.x_request_id, self.log_id, msg)
            else:
                return u"Request {0}: {1}".format(self.x_request_id, msg)
        else:
            if self.log_id is not None:
                return u"Request with Log ID {0}: {1}".format(self.log_id, msg)
            else:
                return msg

    # Returns the underlying `Exception` (base class) message, which is usually
    # the raw message returned by Fintecture's API. This was previously available
    # in python2 via `error.message`. Unlike `str(error)`, it omits "Request
    # req_..." from the beginning of the string.
    @property
    def user_message(self):
        return self._message

    def __repr__(self):
        return "%s(message=%r, url=%r, http_status=%r, log_id=%r, x_request_id=%r, errors=%r)" % (
            self.__class__.__name__,
            self._message,
            self.url,
            self.http_status,
            self.log_id,
            self.x_request_id,
            self.errors
        )

    def construct_error_object(self):
        if (
            self.json_body is None
            or "errors" not in self.json_body
            or not isinstance(self.json_body["errors"], list)
            or len(self.json_body["errors"]) == 0
        ):
            return None

        return fintecture.api_resources.error_object.ErrorObject.construct_from(
            self.json_body,
            fintecture.app_id
        )


class APIError(FintectureError):
    # used when an error occur trying to parse JSON,
    # decoding response data doesn't match documented API scheme, and more
    pass


class APIConnectionError(FintectureError):
    def __init__(
        self,
        message,
        url=None,
        http_body=None,
        http_status=None,
        json_body=None,
        headers=None,
        code=None,
        should_retry=False,
    ):
        super(APIConnectionError, self).__init__(
            message, url, http_body, http_status, json_body, headers, code
        )
        self.should_retry = should_retry


class FintectureErrorWithParamCode(FintectureError):
    def __repr__(self):
        return (
            "%s(message=%r, url=%r, param=%r, code=%r, http_status=%r, log_id=%r, x_request_id=%r)"
            % (
                self.__class__.__name__,
                self._message,
                self.url,
                self.param,
                self.code,
                self.http_status,
                self.log_id,
                self.x_request_id,
            )
        )


class InvalidRequestError(FintectureErrorWithParamCode):
    def __init__(
        self,
        message,
        param,
        code=None,
        http_body=None,
        http_status=None,
        json_body=None,
        headers=None,
    ):
        super(InvalidRequestError, self).__init__(
            message, url, http_body, http_status, json_body, headers, code
        )

        # define the name of invalid parameters separate each one by comma
        self.param = param


class AuthenticationError(FintectureError):
    pass


class BadRequestError(FintectureError):
    pass


class AuthorizationError(FintectureError):
    pass


class PermissionError(FintectureError):
    pass


class NotFoundError(FintectureError):
    pass


class TooManyRequestsError(FintectureError):
    pass


class InternalServerError(FintectureError):
    pass


class ServiceUnavailableError(FintectureError):
    pass


class SignatureVerificationError(FintectureError):
    def __init__(self, message, signature_header, digest_header, request_id_header, http_body=None):
        super(SignatureVerificationError, self).__init__(
            message=message,
            http_body=http_body
        )
        self.sig_header = signature_header
        self.digest_header = digest_header
        self.request_id_header = request_id_header
