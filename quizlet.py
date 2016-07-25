#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse

class QuizletSession():
    """docstring for QuizletSession"""

class _QuizletAuthorizationHTTPHandler(BaseHTTPRequestHandler):
    def do_GET():
        # Set up the web page for the redirect.
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        self.wfile.write("You may close the window now.", "UTF-8")

        # Check to see if user allowed access and Quizlet returned an authorization code
        if "code" in self.path:
            queries   = parse.urlparse(self.path).query
            auth_code = parse.parse_qs(queries)["code"][0]