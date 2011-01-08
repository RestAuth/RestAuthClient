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
Module handling code relevant to user authentication and property management.
"""

try:
	from RestAuthClient import common
	from RestAuthClient.errors import *
except ImportError:
	from errors import *
	import common

class UserExists( ResourceConflict):
	"""
	Thrown when a L{User} that already exists should be created.
	"""
	pass

class PropertyExists( ResourceConflict ):
	"""
	Thrown when trying to create a property that already exists.
	"""
	pass

def create( conn, name, pwd ):
	"""
	Factory method that creates a I{new} user in the RestAuth
	database.
	
	@param conn: A connection to a RestAuth service.
	@type  conn: L{RestAuthConnection}
	@param name: Name of the user to get
	@type  name: str
	@param pwd: Password for the new user
	@type  pwd: str
	@return: The user object representing the user just created.
	@rtype: L{User}
	@raise UserExists: If the user already exists.
	@raise PreconditionFailed: When username or password is invalid.
	@raise InternalServerError: When the RestAuth service returns HTTP
		status code 500
	@raise UnknownStatus: If the response status is unknown.
	"""
	params = { 'user': name, 'password': pwd }
	resp = conn.post( User.prefix, params )
	if resp.status == 201:
		return User( conn, name )
	elif resp.status == 409:
		raise UserExists( name )
	elif resp.status == 412:
		raise PreconditionFailed( resp.read() )
	else:
		raise UnknownStatus( resp )

def get( conn, name ):
	"""
	Factory method that gets an I{existing} user from RestAuth. This
	method verifies that the user exists in the RestAuth and throws
	L{ResourceNotFound} if not. 

	@param conn: A connection to a RestAuth service.
	@type  conn: L{RestAuthConnection}
	@param name: Name of the user to get
	@type  name: str
	@return: The user object representing the user just created.
	@rtype: L{User}
	@raise ResourceNotFound: If the user does not exist in RestAuth.
	@raise InternalServerError: When the RestAuth service returns
		HTTP status code 500
	@raise UnknownStatus: If the response status is unknown.
	"""
	# this just verify that the user exists in RestAuth:
	resp = conn.get( '/users/%s/'%(name) )

	if resp.status == 204:
		return User( conn, name )
	elif resp.status == 404:
		raise ResourceNotFound( resp )
	else:
		raise UnknownStatus( resp )
	
def get_all( conn ):
	"""
	Factory method that gets all users known to RestAuth.

	@param conn: A connection to a RestAuth service.
	@type  conn: L{RestAuthConnection}
	@return: A list of User objects
	@rtype: List of L{users<User>}
	@raise InternalServerError: When the RestAuth service returns HTTP
		status code 500
	@raise UnknownStatus: If the response status is unknown.
	"""
	resp = conn.get( User.prefix )
		
	if resp.status == 200:
		body = resp.read().decode( 'utf-8' )
		usernames = conn.content_handler.unmarshal_list( body )
		return [ User( conn, name ) for name in usernames ]
	else:
		raise UnknownStatus( resp )

class User( common.RestAuthResource ):
	"""
	This class acts as a frontend for actions related to users.
	"""

	#: Prefix used for queries, not used by property related functions
	prefix = '/users/'

	def __init__( self, conn, name ):
		"""
		Constructor that initializes an object representing a user in
		RestAuth. The constructor B{does not} verify if the user exists,
		use L{get} or L{get_all} if you wan't to be sure it exists.
		"""
		self.conn = conn
		self.name = name

	def set_password( self, password ):
		"""
		Set the password of this user.

		@raise ResourceNotFound: If the user does not exist in RestAuth.
		@raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		@raise PreconditionFailed: When the password is invalid.
		"""
		resp = self._put( self.name, { 'password': password } )
		if resp.status == 204:
			return
		elif resp.status == 404:
			raise ResourceNotFound( resp )
		elif resp.status == 412:
			raise PreconditionFailed( resp.read() )
		else:
			raise UnknownStatus( resp )

	def verify_password( self, password ):
		"""
		Verify the given password.

		@param password: The password to verify.
		@type  password: str
		@return: True if the password is correct, False if the password
			is wrong or the user does not exist.
		@rtype: boolean
		@raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		"""
		resp = self._post( self.name, { 'password': password } )
		if resp.status == 204:
			return True
		elif resp.status == 404:
			return False
		else:
			raise UnknownStatus( resp )

	def remove( self ):
		"""
		Remove this user.

		@raise ResourceNotFound: If the user does not exist in RestAuth.
		@raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		"""
		resp = self._delete( self.name )
		if resp.status == 204:
			return
		if resp.status == 404:
			raise ResourceNotFound( resp )
		else:
			raise UnknownStatus( resp )

	def get_properties( self ):
		"""
		Get all properties defined for this user.

		@return: A key/value array of the properties defined for this user.
		@rtype: dict
		@raise ResourceNotFound: If the user does not exist in RestAuth.
		@raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		"""
		resp = self._get( '%s/props/'%(self.name) )
		if resp.status == 200:
			body = resp.read().decode( 'utf-8' )
			return self.conn.content_handler.unmarshal_dict( body )
		elif resp.status == 404:
			raise ResourceNotFound( resp )
		else:
			raise UnknownStatus( resp )

	def create_property( self, prop, value ):
		"""
		Create a new property for this user. This method fails if the
		property already existed. Use L{set_property} if you do not care
		if the property already exists.

		@param prop: The property to set.
		@type  prop: str
		@param value: The new value of the property
		@type  value: str
		@raise ResourceNotFound: If the user does not exist in RestAuth.
		@raise PropertyExists: When the property already exists
		@raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		"""
		params = { 'prop': prop, 'value': value }
		resp = self._post( '%s/props/'%(self.name), params=params )
		if resp.status == 201:
			return
		elif resp.status == 404:
			raise ResourceNotFound( resp )
		elif resp.status == 409:
			raise PropertyExists( resp )
		else:
			raise UnknownStatus( resp )

	def set_property( self, prop, value ):
		"""
		Set a property for this user. This method overwrites any
		previous entry.

		@param prop: The property to set.
		@type  prop: str
		@param value: The new value of the property
		@type  value: str
		@raise ResourceNotFound: If the user does not exist in RestAuth.
		@todo: When the response body contains the previous setting, 
			return that. This is also a todo on the interface side.
		@raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		"""
		url = '%s/props/%s/'%( self.name, prop )
		resp = self._put( url, params={'value': value} )
		if resp.status == 200:
			body = resp.read().decode( 'utf-8' )
			return self.conn.content_handler.unmarshal_str( body )
		if resp.status == 201:
			return
		elif resp.status == 404:
			raise ResourceNotFound( resp )
		else:
			raise UnknownStatus( resp )

	def get_property( self, prop ):
		"""
		Get the given property for this user.

		@return: The value of the property.
		@rtype: str
		@raise ResourceNotFound: If the user or property does not exist.
		@raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		@todo: The distinction between "user not found" and
			"property not found" requires some interface change or
			clarification.
		"""
		resp = self._get( '%s/props/%s'%( self.name, prop ) )
		if resp.status == 200:
			body = resp.read().decode( 'utf-8' )
			return self.conn.content_handler.unmarshal_str( body )
		elif resp.status == 404:
			raise ResourceNotFound( resp )
		else:
			raise UnknownStatus( resp )

	def remove_property( self, prop ):
		"""
		Delete the given property.

		@raise ResourceNotFound: If the user or property does not exist.
		@raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		"""
		resp = self._delete( '%s/props/%s'%(self.name, prop) )
		if resp.status == 204:
			return
		elif resp.status == 404:
			raise ResourceNotFound( resp )
		else:
			raise UnknownStatus( resp )

	def __eq__( self, other ):
		"""
		Two instances of the class User evaluate as equal if their name
		and connection evaluate as equal.
		"""
		return self.name == other.name and self.conn == other.conn
	
	def __hash__( self ):
		return hash( self.name )

	def __repr__( self ):
		import sys
		if sys.version_info < (3, 0) and self.name.__class__ == unicode:
			return '<User: {0}>'.format(self.name.encode( 'utf-8' ))
		else:
			return '<User: {0}>'.format( self.name )
