#!/usr/bin/env python3

import json

from datetime import datetime
from urllib import request


class User:
    """docstring for User"""

    def __init__(self, json, access_token):
        self._raw_json = json
        self._access_token = access_token

        self.username = json["username"]
        self.account_type = json["account_type"]
        self.id_number = json["id"]
        self.signup_date = datetime.fromtimestamp(json["sign_up_date"])
        self.profile_picture = json["profile_image"]
        self.statistics = json["statistics"]
        self.sets = json["sets"]
        self.studied_sets = json["studied"]
        self.classes = json["groups"]

        # cannot access favorites for user not authenticated
        if "favorite_sets" in json.keys():
            self.favorite_sets = json["favorite_sets"]

    def favorite_set_using_id(self, set_id):
        header = {
            "Authorization": "Bearer {}".format(self._access_token)
        }
        api_url = "https://api.quizlet.com/2.0/users/{}/favorites/{}".format(
            self.username, set_id)

        # making a PUT request to favorite set
        qzlt_request = request.Request(api_url, headers=header, method="PUT")
        request.urlopen(qzlt_request)

        return self._get_favorites()

    def favorite_set(self, set):
        self.favorite_set_using_id(set.id)

    def unfavorite_set_using_id(self, set_id):
        header = {
            "Authorization": "Bearer {}".format(self._access_token)
        }
        api_url = "https://api.quizlet.com/2.0/users/{}/favorites/{}".format(
            self.username, set_id)

        # making a DELETE request to favorite set
        qzlt_request = request.Request(api_url, headers=header,
                                       method="DELETE")
        request.urlopen(qzlt_request)

        return self._get_favorites()

    def unfavorite_set(self, set):
        self.unfavorite_set_using_id(set.id)

    def _get_favorites(self):
        header = {
            "Authorization": "Bearer {}".format(self._access_token)
        }
        api_url = "https://api.quizlet.com/2.0/users/{}/favorites".format(
            self.username)

        # making a GET request for favorites
        qzlt_request = request.Request(api_url, headers=header)
        response = request.urlopen(qzlt_request)

        favorites_json = json.loads(response.read().decode("UTF-8"))
        self.favorites = favorites_json

        return favorites_json
