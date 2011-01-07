# This file is part of RestAuthClient.py.
#
#    RestAuthClient.py is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RestAuthClient.py.  If not, see <http://www.gnu.org/licenses/>.

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

class Unauthorized( RestAuthException ):
	"""
	Thrown when service authentication failed.
	"""
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

	On a protocol level, this represents HTTP status code 400.
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

class ContentTypeException( RestAuthInternalException ):
	"""
	Meta-class for Content-Type related exceptions.
	"""
	pass

class NotAcceptable( ContentTypeException ):
	"""
	The current content type is not acceptable to the RestAuth service.
	
	On a protocol level, this represents HTTP status code 406.
	"""
	pass

class UnsupportedMediaType( ContentTypeException ):
	"""
	The RestAuth service does not support the media type used by this client
	implementation.

	On a protocol level, this represents HTTP status code 415.
	"""
	pass

class ResourceNotFound( RestAuthException ):
	"""
	Thrown when a queried resource is not found.
	"""
	def __init__( self, response ):
		self.response = response

	def get_type( self ):
		"""
		Get the type of the queried resource that wasn't found.

		See the U{specification<http://fs.fsinf.at/wiki/RestAuth/Specification#Resource-Type_header>}
		for possible values.
		"""
		return self.response.getheader( 'Resource-Type' )


class ResourceConflict( RestAuthException ):
	"""
	Thrown when trying to create a resource that already exists.

	On a protocol level, this represents HTTP status code 409.
	"""
	pass

class PreconditionFailed( RestAuthException ):
	"""
	Thrown when the submitted data was unacceptable to the system. This
	usually occurs when the username is invalid or the password is to short.
	
	On a protocol level, this represents HTTP status code 412.
	"""
	pass
