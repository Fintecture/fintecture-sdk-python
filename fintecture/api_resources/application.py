from __future__ import absolute_import, division, print_function

from fintecture.api_resources.abstract import SingletonAPIResource


class Application(SingletonAPIResource):
    OBJECT_NAME = "application"

    @classmethod
    def class_url(cls):
        return "/res/v1/applications"
