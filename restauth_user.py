"""
Module handling code relevant to user authentication and property management.
"""

from errors import *
import common

class UserNotFound( ResourceNotFound ):
	"""
	Exception thrown when a L{User} is not found.
	"""
	def __init__( self, response ):
		self.response = response

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

class PropertyNotFound( ResourceNotFound ):
	"""
	Thrown when a property is not found.
	"""
	def __init__( self, response ):
		self.response = response

class User( common.RestAuthResource ):
	"""
	This class acts as a frontend for actions related to users.
	"""

	#: Prefix used for queries, not used by property related functions
	prefix = '/users/'

	@staticmethod
	def create( conn, name, pwd ):
		"""
		Factory method that creates a I{new} user in the RestAuth
		database.

		@return: The user object representing the user just created.
		@rtype: L{User}
		@raise UserExists: If the user already exists.
		@raise BadRequest: When the username or password is unacceptable to RestAuth.
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		"""
		params = { 'user': name, 'password': pwd }
		resp = conn.post( User.prefix, params )
		if resp.status == 201:
			return User( conn, name )
		elif resp.status == 409:
			raise UserExists( name )
		else:
			raise UnknownStatus( resp.status )

	@staticmethod
	def get( conn, name ):
		"""
		Factory method that gets an I{existing} user from RestAuth. This
		method verifies that the user exists in the RestAuth and throws
		L{UserNotFound} if not. 

		@return: The user object representing the user just created.
		@rtype: L{User}
		@raise UserNotFound: If the user does not exist in RestAuth.
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		"""
		# this just verify that the user exists in RestAuth:
		resp = conn.get( '/users/%s/'%(name) )

		if resp.status == 200:
			return User( conn, name )
		elif resp.status == 404:
			raise UserNotFound( name )
		else:
			raise UnknownStatus( resp )
	
	@staticmethod
	def get_all( conn ):
		"""
		Factory method that gets all users known to RestAuth.

		@return: A list of User objects
		@rtype: List of L{users<User>}
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		"""
		resp = conn.get( User.prefix )
		
		if resp.status == 200:
			import json
			users = []
			body = resp.read().decode( 'utf-8' )
			usernames = json.loads( body )
			for name in usernames:
				users.append( User( conn, name ) )
			return users
		else:
			raise UnknownStatus( resp )

	def __init__( self, conn, name ):
		"""
		Constructor that initializes an object representing a user in
		RestAuth. The constructor B{does not} verify if the user exists,
		use L{get} or L{get_all} if you wan't to be sure it exists.
		"""
		self.conn = conn
		self.name = name

	def set_password( self, pwd ):
		"""
		Set the password of the given user.

		@raise UserNotFound: If the user does not exist in RestAuth.
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		"""
		resp = self._put( self.name, { 'password': pwd } )
		if resp.status == 200:
			return
		elif resp.status == 404:
			raise UserNotFound( self.name )
		else:
			raise UnknownStatus( resp )

	def verify_password( self, pwd ):
		"""
		Verify the given password.

		@return: True if the password is correct, False if the password
			is wrong or the user does not exist.
		@rtype: boolean
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		"""
		resp = self._post( self.name, { 'password': pwd } )
		if resp.status == 200:
			return True
		elif resp.status == 404:
			return False
		else:
			raise UnknownStatus( resp )

	def delete( self ):
		"""
		Delete this user.

		@raise UserNotFound: If the user does not exist in RestAuth.
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		"""
		resp = self._delete( self.name )
		if resp.status == 200:
			return
		if resp.status == 404:
			raise UserNotFound( self.name )
		else:
			raise UnknownStatus( resp )

	def get_properties( self ):
		"""
		Get all properties defined for this user.

		@return: A dictionary containing key/value pairs.
		@rtype: dict
		@raise UserNotFound: If the user does not exist in RestAuth.
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		"""
		resp = self._get( self.name, prefix='/userprops/' )
		if resp.status == 200:
			import json
			props = json.loads( resp.read().decode( 'utf-8' ) )
			return props
		elif resp.status == 404:
			raise UserNotFound( self.name )
		else:
			raise UnknownStatus( resp )

	def create_property( self, prop, value ):
		"""
		Create a new property for this user. This method fails if the
		property already existed. Use L{set_property} if you do not care
		if the property already exists.

		@raise UserNotFound: If the user does not exist in RestAuth.
		@raise PropertyExists: When the property already exists
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		"""
		params = { 'prop': prop, 'value': value }
		resp = self._post( self.name, params=params, prefix='/userprops/' )
		if resp.status == 200:
			return
		elif resp.status == 404:
			raise UserNotFound( self.name )
		elif resp.status == 409:
			raise PropertyExists( resp )
		else:
			raise UnknownStatus( resp )

	def set_property( self, prop, value ):
		"""
		Set a property for this user. This method overwrites any
		previous entry.

		@raise UserNotFound: If the user does not exist in RestAuth.
		@todo: When the response body contains the previous setting, 
			return that. This is also a todo on the interface side.
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		"""
		params = { 'value': value }
		url = '%s/%s'%( self.name, prop )
		resp = self._put( url, params=params, prefix='/userprops/' )
		if resp.status == 200:
			return
		elif resp.status == 404:
			raise UserNotFound( self.name )
		else:
			raise UnknownStatus( resp )

	def get_property( self, prop ):
		"""
		Get the given property for this user.

		@return: The value of the property.
		@rtype: str
		@raise UserNotFound: If the user does not exist.
		@raise PropertyNotFound: If the property does not exist.
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		@todo: The distinction between "user not found" and
			"property not found" requires some interface change or
			clarification.
		"""
		url = '%s/%s'%( self.name, prop )
		resp = self._get( url, prefix='/userprops/' )
		if resp.status == 200:
			return resp.read().decode( 'utf-8' )
		elif resp.status == 404:
			typ = resp.getheader( 'Resource' )
			if typ == 'User':
				raise UserNotFound( self.name )
			elif typ == 'Property':
				raise PropertyNotFound( prop )
			else:
				raise RuntimeError( 'Received wrong response header!' )
		else:
			raise UnknownStatus( resp )

	def del_property( self, prop ):
		"""
		Delete the given property.

		@raise UserNotFound: If the user does not exist in RestAuth.
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@raise UnknownStatus: If the response status is unknown.
		"""
		url = '%s/%s'%( self.name, prop )
		resp = self._delete( url, prefix='/userprops/' )
		if resp.status == 200:
			return
		elif resp.status == 404:
			raise UserNotFound( self.name )
		else:
			raise UnknownStatus( resp )

	def __eq__( self, other ):
		"""
		@todo: compare connection
		"""
		return self.name == other.name
	
	def __hash__( self ):
		return hash( self.name )

	def __repr__( self ):
		return '<User: %s>'%(self.name)
