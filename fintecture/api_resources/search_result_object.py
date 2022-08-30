from __future__ import absolute_import, division, print_function

from fintecture import six
from fintecture.fintecture_object import FintectureObject


class SearchResultObject(FintectureObject):
    OBJECT_NAME = "search_result"

    def search(
        self, app_id=None, fintecture_version=None, **params
    ):
        return self._request(
            "get",
            self.get("url"),
            app_id=app_id,
            fintecture_version=fintecture_version,
            params=params,
        )

    def __getitem__(self, k):
        if isinstance(k, six.string_types):
            return super(SearchResultObject, self).__getitem__(k)
        else:
            raise KeyError(
                "You tried to access the %s index, but SearchResultObject types "
                "only support string keys. (HINT: Search calls return an object "
                "with  a 'data' (which is the data array). You likely want to "
                "call .data[%s])" % (repr(k), repr(k))
            )

    def __iter__(self):
        return getattr(self, "data", []).__iter__()

    def __len__(self):
        return getattr(self, "data", []).__len__()

    def auto_paging_iter(self):
        page = self

        while True:
            for item in page:
                yield item
            page = page.next_search_result_page()

            if page.is_empty:
                break

    @classmethod
    def empty_search_result(
        cls, app_id=None, fintecture_version=None
    ):
        return cls.construct_from(
            {"data": [], "has_more": False, "next_page": None},
            app_id=app_id,
            fintecture_version=fintecture_version,
            last_response=None,
        )

    @property
    def is_empty(self):
        return not self.data

    def next_search_result_page(
        self, app_id=None, fintecture_version=None, **params
    ):
        if not self.has_more:
            return self.empty_search_result(
                app_id=app_id,
                fintecture_version=fintecture_version,
            )

        params_with_filters = self._retrieve_params.copy()
        params_with_filters.update({"page": self.next_page})
        params_with_filters.update(params)

        return self.search(
            app_id=app_id,
            fintecture_version=fintecture_version,
            **params_with_filters
        )
