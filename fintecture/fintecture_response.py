from __future__ import absolute_import, division, print_function

import json
from collections import OrderedDict


class FintectureResponseBase(object):
    def __init__(self, url, code, headers):
        self.url = url
        self.code = code
        self.headers = headers

    @property
    def x_request_id(self):
        try:
            return self.headers["x-request-id"]
        except KeyError:
            return None


class FintectureResponse(FintectureResponseBase):
    def __init__(self, url, body, code, headers):
        FintectureResponseBase.__init__(self, url, code, headers)
        self.body = body
        try:
            self.data = json.loads(body, object_pairs_hook=OrderedDict)
        except Exception as e:
            # keep Fintecture error format
            self.data = {
                'status': code,
                'code': 'internal_invalid_json',
                'errors': [
                    {
                        'code': 'internal_invalid_json',
                        'title': 'Invalid JSON',
                        'message': 'Received JSON content has an invalid format',
                    }
                ]
            }
