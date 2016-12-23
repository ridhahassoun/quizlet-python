#!/usr/bin/env python3

from datetime import datetime


class User():
    """docstring for User"""

    def __init__(self, json=None):
        if json:
            self._raw_json = json

            self.username = json["username"]
            self.account_type = json["account_type"]
            self.id_number = json["id"]
            self.signup_date = datetime.fromtimestamp(json["sign_up_date"])
            self.profile_picture = json["profile_image"]
            self.statistics = json["statistics"]
            self.sets = json["sets"]
            self.favorite_sets = json["favorite_sets"]
            self.studied_sets = json["studied"]
            self.classes = json["groups"]
