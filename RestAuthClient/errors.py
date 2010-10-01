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

class ResourceNotFound( RestAuthException ):
	"""
	Common base class for resources (L{users<user.User>}, 
	L{groups<Group.Group>} or properties) not found.
	"""
	def __init__( self, response, resource_class ):
		self.response = response
		self.resource_class = resource_class

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

class ResourceConflict( RestAuthException ):
	"""
	Thrown when trying to create a resource that already exists.

	On a protocol level, this represents HTTP status code 409.
	"""
	pass

class DataUnacceptable( RestAuthException ):
	"""
	Thrown when the submitted data was unacceptable to the system. This
	usually occurs when the username is invalid or the password is to short.
	"""
	pass
