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
	Common base class for resources (L{users<user.User>}, L{groups<Group.Group>}) not found.
	"""
	def __init__( self, response, resource_class ):
		self.response = response
		self.resource_class = resource_class
	pass

class RestAuthInternalException( RestAuthException ):
	"""
	Base class for errors internal to RestAuth and where the error is not
	related to user input.
	"""
	def __init__( self, response ):
		self.response = response

class BadRequest( RestAuthInternalException ):
	"""
	Thrown when RestAuth was unable to parse/find the required request
	parameters. 

	This exception is only thrown when using either the POST or PUT HTTP
	methods.
	"""
	pass

class InternalServerError( RestAuthInternalException ):
	"""
	Thrown when the RestAuth service has an Internal Server Error (HTTP
	status code 500). 
	
	This exception can be thrown by every method that interacts with the
	RestAuth service.
	"""
	pass

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
