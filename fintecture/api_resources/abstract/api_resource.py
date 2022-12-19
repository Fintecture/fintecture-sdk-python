from __future__ import absolute_import, division, print_function

from fintecture import api_requestor, error, util, six
from fintecture.fintecture_object import FintectureObject
from fintecture.six.moves.urllib.parse import quote_plus


class APIResource(FintectureObject):
    @classmethod
    def retrieve(cls, id, app_id=None, **params):
        instance = cls(id, app_id, **params)
        instance.refresh()
        return instance

    def refresh(self):
        return self._request_and_refresh("get", self.instance_url())

    @classmethod
    def class_url(cls):
        if cls == APIResource:
            raise NotImplementedError(
                "APIResource is an abstract class.  You should perform "
                "actions on its subclasses (e.g. Charge, Customer)"
            )
        # Namespaces are separated in object names with periods (.) and in URLs
        # with forward slashes (/), so replace the former with the latter.
        base = cls.OBJECT_NAME.replace(".", "/")
        return "/v1/%ss" % (base,)

    def instance_url(self):
        id = self.get("id")

        if not isinstance(id, six.string_types):
            raise error.InvalidRequestError(
                "Could not determine which URL to request: %s instance "
                "has invalid ID: %r, %s. ID should be of type `str` (or"
                " `unicode`)" % (type(self).__name__, id, type(id)),
                "id",
            )

        id = util.utf8(id)
        base = self.class_url()
        extn = quote_plus(id)
        return "%s/%s" % (base, extn)

    # The `method_` and `url_` arguments are suffixed with an underscore to
    # avoid conflicting with actual request parameters in `params`.
    def _request(
        self,
        method_,
        url_,
        app_id=None,
        fintecture_version=None,
        headers=None,
        params=None,
    ):
        obj = FintectureObject._request(
            self,
            method_,
            url_,
            app_id,
            fintecture_version,
            headers,
            params,
        )

        if type(self) is type(obj):
            self.refresh_from(obj)
            return self
        else:
            return obj

    # The `method_` and `url_` arguments are suffixed with an underscore to
    # avoid conflicting with actual request parameters in `params`.
    def _request_and_refresh(
        self,
        method_,
        url_,
        app_id=None,
        fintecture_version=None,
        headers=None,
        params=None,
    ):
        obj = FintectureObject._request(
            self,
            method_,
            url_,
            app_id,
            fintecture_version,
            headers,
            params,
        )

        self.refresh_from(obj)
        return self

    # The `method_` and `url_` arguments are suffixed with an underscore to
    # avoid conflicting with actual request parameters in `params`.
    @classmethod
    def _static_request(
        cls,
        method_,
        url_,
        app_id=None,
        fintecture_version=None,
        params=None,
    ):
        params = None if params is None else params.copy()
        fintecture_version = util.read_special_variable(
            params, "fintecture_version", fintecture_version
        )
        fintecture_app_id = util.read_special_variable(
            params, "app_id", app_id
        )
        fintecture_app_secret = util.read_special_variable(
            params, "app_secret", None
        )
        fintecture_private_key = util.read_special_variable(
            params, "private_key", None
        )
        headers = util.read_special_variable(params, "headers", None)

        requestor = api_requestor.APIRequestor(
            app_id=fintecture_app_id,
            app_secret=fintecture_app_secret,
            private_key=fintecture_private_key,
            api_version=fintecture_version,
        )

        response, my_app_id = requestor.request(method_, url_, params, headers)
        return util.convert_to_fintecture_object(
            response, my_app_id, fintecture_version, params
        )
