from __future__ import absolute_import, division, print_function

from fintecture import util
from fintecture.api_resources.abstract.api_resource import APIResource
from fintecture.six.moves.urllib.parse import quote_plus


class UpdateableAPIResource(APIResource):
    @classmethod
    def modify(cls, sid, **params):
        url = "%s/%s" % (cls.class_url(), quote_plus(util.utf8(sid)))
        return cls._static_request("post", url, params=params)

    def save(self):
        updated_params = self.serialize(None)
        if updated_params:
            self._request_and_refresh(
                "post",
                self.instance_url(),
                params=updated_params,
            )
        else:
            util.logger.debug("Trying to save already saved object %r", self)
        return self
