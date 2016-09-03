#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse, request
from uuid import uuid4
import webbrowser
import base64
import json

import errors

class QuizletSession():
    """docstring for QuizletSession"""
    def __init__(self, client_id, client_secret, scope="read"):
        self._client_id = client_id
        self._client_secret = client_secret

        state = str(uuid4()) # generate a string to send and receive to verify and prevent CSRF attacks

        # Check to see if scopes requested are valid
        valid_scopes = ["read", "write_set", "write_group"]
        invalid_scopes = [inv for inv in scope.split(" ") if inv not in valid_scopes]

        # If invalid scopes are present, end OAuth2 flow and raise ScopeError
        if invalid_scopes: raise errors.ScopeError(invalid_scopes)

        url = self._make_authorization_url(self._client_id, state, scope)
        webbrowser.open_new(url)

        server = HTTPServer(('', 8000), _QuizletAuthorizationHTTPHandler)
        server.data = (self._client_id, self._client_secret, state)
        server.handle_request()

        access_token_json = server.access_token
        self._user_id = access_token_json["user_id"]
        self._access_token = access_token_json["access_token"]

    def _make_authorization_url(self, client_id, state, scope):
        params = {
            "client_id": client_id,
            "response_type": "code",
            "state": state,
            "scope": scope
        }
        url = "https://quizlet.com/authorize?" + parse.urlencode(params)

        return url

    # Properties
    @property
    def client_id(self):
        return self._client_id

    @property
    def client_secret(self):
        return self._client_secret

    @property
    def user_id(self):
        return self._user_id
    
    @property
    def access_token(self):
        return self._access_token

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

        # Check to see if user allowed access and Quizlet returned an authorization code
        if "code" in self.path:
            queries = parse.urlparse(self.path).query
            client_id, client_secret, state = self.server.data

            # make sure the state we sent is the same as the state returned
            if parse.parse_qs(queries)["state"][0] == state: 
                auth_code = parse.parse_qs(queries)["code"][0]

                access_token = self._get_access_token(client_id, client_secret, auth_code)
                #TODO: parsing error if returned
                self.server.access_token = access_token

    # to remove logging to console every time a request is made
    def log_message(self, format, *args): 
        return

    def _get_access_token(self, client_id, client_secret, authorization_code):
        base64string = base64.b64encode(bytes("{}:{}".format(client_id, client_secret), "UTF-8"))
        header = {"Authorization": "Basic {}".format(base64string.decode("UTF-8"))}
        post_data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": "http://localhost:8000/"
        }
        data = parse.urlencode(post_data).encode("UTF-8")

        quizlet_request = request.Request("https://api.quizlet.com/oauth/token",
                                          data=data,
                                          headers=header)

        response = request.urlopen(quizlet_request)

        token_json = json.loads(response.read().decode("UTF-8"))
        return token_json