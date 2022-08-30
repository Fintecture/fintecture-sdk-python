from __future__ import absolute_import, division, print_function

from fintecture.util import merge_dicts
from fintecture.fintecture_object import FintectureObject


class ErrorObject(FintectureObject):
    def refresh_from(
        self,
        values,
        app_id=None,
        fintecture_version=None,
        last_response=None,
    ):
        # Unlike most other API resources, the API will omit attributes in
        # error objects when they have a null value. We manually set default
        # values here to facilitate generic error handling.
        values = merge_dicts(
            {
                "status": None,
                "code": None,
                "log_id": None,
                "errors": [],
            },
            values,
        )
        return super(ErrorObject, self).refresh_from(
            values,
            app_id,
            fintecture_version,
            last_response,
        )
