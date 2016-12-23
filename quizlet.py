#!/usr/bin/env python3

import base64
import json
import uuid
import webbrowser

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse, request

import errors
import users


class QuizletSession():
    """docstring for QuizletSession"""

    def __init__(self, client_id, client_secret, scope="read"):
        self._client_id = client_id
        self._client_secret = client_secret

        # Generate string to send and receive to verify request
        state = str(uuid.uuid4())

        # Check to see if scopes requested are valid
        valid_scopes = ["read", "write_set", "write_group"]
        invalid_scopes = [inv for inv in scope.split(" ")
                          if inv not in valid_scopes]

        # If invalid scopes are present, end OAuth2 flow and raise ScopeError
        if invalid_scopes:
            raise errors.ScopeError(invalid_scopes)

        # Prepare authorization URL for OAuth2 flow
        url = self._make_authorization_url(self._client_id, state, scope)
        webbrowser.open_new(url)

        # Set up local server to receive redirect and handle it
        server = HTTPServer(('', 8000), _QuizletAuthorizationHTTPHandler)
        server.data = (self._client_id, self._client_secret, state)
        server.handle_request()

        # After handle_request() completes, retrieve access token
        access_token_json = server.access_token
        self.user_id = access_token_json["user_id"]
        self.access_token = access_token_json["access_token"]
        self.expiration = access_token_json["expires_in"]

    @classmethod
    def using_access_token(cls, user_id, access_token):
        """Creates a new session without going through OAuth2 flow.
        Requires both user's user ID and access token."""

        session = super().__new__(cls)
        session.user_id = user_id
        session.access_token = access_token
        return session

    def get_current_user(self):
        """Returns the current authenticated user."""

        header = {
            "Authorization": "Bearer {}".format(self.access_token)
        }
        api_url = "https://api.quizlet.com/2.0/users/{}".format(self.user_id)

        # making a GET request for current user
        qzlt_request = request.Request(api_url, headers=header)
        response = request.urlopen(qzlt_request)
        user_json = json.loads(response.read().decode("UTF-8"))

        current_user = users.User(json=user_json)
        return current_user

    def _make_authorization_url(self, client_id, state, scope):
        params = {
            "client_id": client_id,
            "response_type": "code",
            "state": state,
            "scope": scope
        }
        url = "https://quizlet.com/authorize?" + parse.urlencode(params)

        return url


class _QuizletAuthorizationHTTPHandler(BaseHTTPRequestHandler):
    """A subclass of BaseHTTPRequestHandler that is used internally
    to help manage the redirect from Quizlet and complete the
    authentication process.

    This class should not be called directly."""

    def do_GET(self):
        # Set up the web page for the redirect.
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        self.wfile.write(bytes("You may close the window now.", "UTF-8"))

        # Check to see if user allowed access and Quizlet returned an
        # authorization code
        if "code" in self.path:
            queries = parse.urlparse(self.path).query
            client_id, client_secret, state = self.server.data

            # make sure the state we sent is the same as the state returned
            if parse.parse_qs(queries)["state"][0] == state:
                auth_code = parse.parse_qs(queries)["code"][0]

                access_token = self._get_access_token(client_id, client_secret,
                                                      auth_code)
                # TODO: parsing error if returned
                self.server.access_token = access_token

    # to remove logging to console every time a request is made
    def log_message(self, format, *args):
        return

    def _get_access_token(self, client_id, client_secret, authorization_code):
        """This function sets up POST request for access token and then requests
        it. It returns access token provided by Quizlet after OAuth2 flow
        has completed."""

        base64string = base64.b64encode(
            bytes("{}:{}".format(client_id, client_secret), "UTF-8"))
        header = {
            "Authorization": "Basic {}".format(base64string.decode("UTF-8"))
        }
        post_data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": "http://localhost:8000/"
        }
        data = parse.urlencode(post_data).encode("UTF-8")

        # making a POST request to get access token
        qzlt_request = request.Request("https://api.quizlet.com/oauth/token",
                                       data=data,
                                       headers=header)

        response = request.urlopen(qzlt_request)

        token_json = json.loads(response.read().decode("UTF-8"))
        return token_json
