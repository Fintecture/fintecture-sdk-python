from __future__ import absolute_import, division, print_function


class VerifyMixin(object):
    def verify(self, **params):
        url = self.instance_url() + "/verify"
        return self._request(
            "post", url, params=params
        )
