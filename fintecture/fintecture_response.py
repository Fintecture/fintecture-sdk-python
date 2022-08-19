from __future__ import absolute_import, division, print_function

import json
from collections import OrderedDict


class FintectureResponseBase(object):
    def __init__(self, code, headers):
        self.code = code
        self.headers = headers

    @property
    def idempotency_key(self):
        try:
            return self.headers["idempotency-key"]
        except KeyError:
            return None

    @property
    def request_id(self):
        try:
            return self.headers["request-id"]
        except KeyError:
            return None


class FintectureResponse(FintectureResponseBase):
    def __init__(self, body, code, headers):
        FintectureResponseBase.__init__(self, code, headers)
        self.body = body
        try:
            self.data = json.loads(body, object_pairs_hook=OrderedDict)
        except Exception as e:
            # keep Fintecture error format
            self.data = {
                'errors': [
                    {
                        'code': 'internal_invalid_json',
                        'title': 'Invalid JSON',
                        'message': 'Received JSON content has an invalid format',
                    }
                ]
            }


class FintectureStreamResponse(FintectureResponseBase):
    def __init__(self, io, code, headers):
        FintectureResponseBase.__init__(self, code, headers)
        self.io = io
