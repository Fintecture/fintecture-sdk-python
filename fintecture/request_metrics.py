from __future__ import absolute_import, division, print_function


class RequestMetrics(object):
    def __init__(self, x_request_id, request_duration_ms):
        self.x_request_id = x_request_id
        self.request_duration_ms = request_duration_ms

    def payload(self):
        return {
            "x_request_id": self.x_request_id,
            "request_duration_ms": self.request_duration_ms,
        }
