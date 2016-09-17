#!/usr/bin/env python3

from datetime import datetime


class User():
    """docstring for User"""

    def __init__(self, json=None):
        if json:
            self._raw_json = json

            self._username = json["username"]
            self._account_type = json["account_type"]
            self._id_number = json["id"]
            self._signup_date = datetime.fromtimestamp(json["sign_up_date"])
            self._profile_picture = json["profile_image"]
            self._statistics = json["statistics"]
            self._sets = json["sets"]
            self._favorite_sets = json["favorite_sets"]
            self._studied_sets = json["studied"]
            self._groups = json["groups"]
