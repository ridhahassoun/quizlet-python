#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse
from uuid import uuid4
import requests
import webbrowser

class QuizletSession():
    """docstring for QuizletSession"""
    def __init__(self, scope="read"):
        state = str(uuid4()) # generate a string to send and receive to verify and prevent CSRF attacks
        print(state)

        url = _make_authorization_url(state, scope)
        webbrowser.open_new(url)

        server = HTTPServer(('', 8000), _QuizletAuthorizationHTTPHandler)
        server.sent_state = state

        server.handle_request()

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
            
            # make sure the state we sent is the same as the state returned
            if parse.parse_qs(queries)["state"][0] == self.server.sent_state: 
                auth_code = parse.parse_qs(queries)["code"][0]

                access_token = _get_access_token(auth_code)
                print(access_token)

def _make_authorization_url(state, scope):
    params = {"client_id": CLIENT_ID,
              "response_type": "code",
              "state": state,
              "scope": scope}
    url = "https://quizlet.com/authorize?" + parse.urlencode(params)

    # convoluted return statement to return a named tuple, for better readability
    # state is also returned in order to verify with the state Quizlet's API returns
    return url

def _get_access_token(authorization_code):
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {"grant_type": "authorization_code",
                 "code": authorization_code,
                 "redirect_uri": "http://localhost:8000/"
    }
    response = requests.post("https://api.quizlet.com/oauth/token", auth=client_auth, data=post_data)
    token_json = response.json()
    return token_json