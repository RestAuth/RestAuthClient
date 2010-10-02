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
Module handling code relevant to group handling.
"""
import json

try:
	from RestAuthClient import common, restauth_user
	from RestAuthClient.errors import *
except ImportError:
	import common, restauth_user
	from errors import *

class GroupNotFound( ResourceNotFound ):
	"""
	Exception thrown when a L{Group} is not found.
	"""
	def __init__( self, response ):
		self.response = response
		self.resource_class = Group

class GroupExists( ResourceConflict ):
	"""
	Thrown when a L{Group} that already exists should be created.
	"""
	pass

def create( conn, name ):
	"""
	Factory method that creates a I{new} group in RestAuth.

	@param conn: A connection to a RestAuth service.
	@type  conn: L{RestAuthConnection}
	@param name: The name of the group to create
	@type  name: str
	@return: The group object representing the group just created.
	@rtype: Group
	@raise GroupExists: When the user already exists.
	@raise BadRequest: When the RestAuth service returns HTTP status code 400
	@raise InternalServerError: When the RestAuth service returns HTTP status code 500
	"""
	resp = conn.post( Group.prefix, { 'group': name } )
	if resp.status == 201:
		return Group( conn, name )
	elif resp.status == 409:
		raise GroupExists( "Conflict." )
	else:
		raise UnknownStatus( resp )

def get_all( conn, user=None, recursive=True ):
	"""
	Factory method that gets all groups for this service known to
	RestAuth.

	@param conn: A connection to a RestAuth service.
	@type  conn: L{RestAuthConnection}
	@param user: Only return groups where the named user is a member
	@type  user: str
	@param recursive: Disable recursive group parsing
	@type  recursive: bool
	@return: A list of Group objects
	@rtype: List of L{groups<Group>}
	@raise BadRequest: When the RestAuth service returns HTTP status code 400
	@raise InternalServerError: When the RestAuth service returns HTTP status code 500
	"""
	params = {}
	if user:
		params['user'] = user
	if not recursive:
		params['nonrecursive'] = 1

	resp = conn.get( Group.prefix, params )
	if resp.status == 200:
		body = resp.read().decode( 'utf-8' )
		names = json.loads( body )
		return [ Group( conn, name ) for name in names ]
	else:
		raise UnknownStatus( resp )

def get( conn, name ):
	"""
	Factory method that gets an I{existing} user from RestAuth. This
	method verifies that the user exists in the RestAuth and throws
	L{UserNotFound} if not. 

	@param conn: A connection to a RestAuth service.
	@type  conn: L{RestAuthConnection}
	@param name: The name of the group to get
	@type  name: str
	@return: The group object representing the group in RestAuth.
	@rtype: L{Group}
	@raise GroupNotFound: If the group does not exist in RestAuth.
	@raise BadRequest: When the RestAuth service returns HTTP status code 400
	@raise InternalServerError: When the RestAuth service returns HTTP status code 500
	"""
	all_groups = get_all( conn )
	g = Group( conn, name )
	if g in all_groups:
		return g
	else:
		raise GroupNotFound( name )

class Group( common.RestAuthResource ):
	prefix = '/groups/'

	def __init__( self, conn, name ):
		"""
		Constructor that initializes an object representing a group in
		RestAuth. The constructor B{does not} verify if the group exists,
		use L{get} or L{get_all} if you wan't to be sure it exists.
		"""
		self.conn = conn
		self.name = name

	def get_members( self, recursive=True ):
		"""
		Get all members of this group.
		
		@param recursive: Set to False to exclude memberships inherited
			from other groups.
		@type  recursive: boolean
		@return: A list of L{users<User>}.
		@rtype: list
		@raise GroupNotFound: If the group does not exist.
		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		"""
		params = {}
		if not recursive:
			params['nonrecursive'] = 1

		resp = self._get( self.name, params )
		if resp.status == 200:
			# parse user-list:
			names = json.loads( resp.read().decode( 'utf-8' ) )
			users = [ restauth_user.User( self.conn, name ) for name in names ]
			return users
		elif resp.status == 404:
			raise GroupNotFound( name )
		else:
			raise UnknownStatus( resp )

	def add_user( self, user, autocreate=True ):
		"""
		Add a user to this group.

		@param user: The user to add.
		@type  user: L{user}
		@param autocreate: Set to False if you not want to automatically
			create the group.
		@raise GroupNotFound: If the group does not exists and autocreate=False.
		@raise UserNotFound: If the user does not exist.
		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@todo: It should be possible that user is a str.
		"""
		params = { 'user': user.name }
		if autocreate:
			params['autocreate'] = 1

		resp = self._post( self.name, params )
		if resp.status == 200:
			return
		elif resp.status == 404:
			try:
				typ = resp.getheader( 'Resource' )
				if typ == 'User':
					raise restauth_user.UserNotFound( resp )
				elif typ == 'Group':
					raise GroupNotFound( resp )
				else:
					raise RuntimeError('Received wrong response header!')
			except TypeError:
				body = resp.read().decode( 'utf-8' ).replace( '\n', "\n" )
				print( body )
		else:
			raise UnknownStatus( resp )

	def add_group( self, group, autocreate=True ):
		"""
		Add a group to this group.
		
		@param group: The group to add.
		@type  group: L{Group}
		@param autocreate: Set to False if you not want to automatically
			create the (parent) group.
		@raise GroupNotFound: If the child group is not found or if the
			parent group does not exists and autocreate=False
		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@todo: It should be possible that group is a str.
		"""
		params = { 'group': group.name }
		if autocreate:
			params['autocreate'] = 1
		
		resp = self._post( self.name, params )
		if resp.status == 200:
			return
		elif resp.status == 404:
			raise GroupNotFound( self.name )
		else:
			raise UnknownStatus( resp )

	def delete( self ):
		"""
		Delete this group.
		
		@raise GroupNotFound: If the group does not exist.
		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		"""
		resp = self._delete( self.name )
		if resp.status == 200:
			return
		elif resp.status == 404:
			raise GroupNotFound( name )
		else:
			raise UnknownStatus( resp )

	def is_member( self, user ):
		"""
		Check if the named user is a member.
		
		@param user: The user in question.
		@type  user: L{User}
		@raise GroupNotFound: If the group does not exist.
		@raise UserNotFound: If the user does not exist.
		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@todo: It should be possible that user is a str.
		"""
		params = { 'user': user.name }

		resp = self._post( self.name, params )
		if resp.status == 200:
			return
		elif resp.status == 404:
			typ = resp.getheader( 'Resource' )
			if typ == 'User':
				raise restauth_user.UserNotFound( resp )
			elif typ == 'Group':
				raise GroupNotFound( resp )
			else:
				raise RuntimeError('Received wrong response header!')
		else:
			raise UnknownStatus( resp )

	def remove_user( self, user ):
		"""
		Remove the given user from the group.

		@raise GroupNotFound: If the group does not exist.
		@raise UserNotFound: If the user does not exist.
		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@todo: It should be possible that user is a str.
		"""
		resp = self._delete( '%s/%s'%(self.name, user.name), 'DELETE' )
		if resp.status == 200:
			return
		elif resp.status == 404:
			typ = resp.getheader( 'Resource' )
			if typ == 'User':
				raise restauth_user.UserNotFound( resp )
			elif typ == 'Group':
				raise GroupNotFound( resp )
			else:
				raise RuntimeError('Received wrong response header!')
		else:
			raise UnknownStatus( resp )

	def __eq__( self, other ):
		return self.name == other.name

	def __repr__( self ):
		return '<Group: %s>'%(self.name)
