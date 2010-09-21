"""
This module collects various general exceptions that might be thrown on many 
different (or all) RestAuth methods.
"""

class RestAuthException( Exception ):
	"""
	Common base class for all RestAuth related exceptions.
	"""
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class ResourceNotFound( RestAuthException ):
	"""
	Common base class for resources (L{users<User.User>}, L{groups<Group.Group>}) not found.
	"""
	pass

class RestAuthInternalException( RestAuthException ):
	"""
	Base class for errors internal to RestAuth and where the error is not
	related to user input.
	"""
	def __init__( self, status, body ):
		self.status = status
		self.body = body

class BadRequest( RestAuthInternalException ):
	"""
	Thrown when RestAuth was unable to parse/find the required request
	parameters. 

	This exception is only thrown when using either the POST or PUT HTTP
	methods.
	"""
	def __init__( self, requ_body, resp_body ):
		self.requ_body = requ_body
		self.resp_body = resp_body 

class InternalServerError( RestAuthInternalException ):
	"""
	Thrown when the RestAuth service has an Internal Server Error (HTTP
	status code 500). 
	
	This exception can be thrown by every method that interacts with the
	RestAuth service.
	"""
	def __init__( self, body ):
		self.status = 500
		self.body = body 

class UnknownStatus( RestAuthInternalException ):
	"""
	Thrown when a method returns an unexpected status.
	
	This exception can be thrown by every method that interacts with the
	RestAuth service.
	"""
	pass

class ResourceConflict( RestAuthException ):
	"""
	Thrown when trying to create a resource that already exists.
	"""
	pass
