#!/usr/bin/env python3

class Error(Exception):
	pass

class ScopeError(Error):
	def __init__(self, invalid_scopes):
		self.invalid_scopes = invalid_scopes

	def __str__(self):
		error = "The following scopes are invalid: {}. Consult with Quizlet API for correct scopes.".format(', '.join(self.invalid_scopes))
		return repr(error)