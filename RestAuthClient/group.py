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
try:
	from RestAuthClient import common, restauth_user
	from RestAuthClient.errors import *
except ImportError:
	import common, restauth_user
	from errors import *

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
	elif resp.status == 412:
		raise PreconditionFailed( resp )
	else:
		raise UnknownStatus( resp )

def get_all( conn, user=None ):
	"""
	Factory method that gets all groups for this service known to
	RestAuth.

	@param conn: A connection to a RestAuth service.
	@type  conn: L{RestAuthConnection}
	@param user: Only return groups where the named user is a member
	@type  user: str
	@return: A list of Group objects
	@rtype: List of L{groups<Group>}
	@raise BadRequest: When the RestAuth service returns HTTP status code 400
	@raise InternalServerError: When the RestAuth service returns HTTP status code 500
	"""
	params = {}
	if user:
		params['user'] = user

	resp = conn.get( Group.prefix, params )
	if resp.status == 200:
		body = resp.read().decode( 'utf-8' )
		names = conn.content_handler.unmarshal_list( body )
		return [ Group( conn, name ) for name in names ]
	else:
		raise UnknownStatus( resp )

def get( conn, name ):
	"""
	Factory method that gets an I{existing} user from RestAuth. This
	method verifies that the user exists in the RestAuth and throws
	L{ResourceNotFound} if not. 

	@param conn: A connection to a RestAuth service.
	@type  conn: L{RestAuthConnection}
	@param name: The name of the group to get
	@type  name: str
	@return: The group object representing the group in RestAuth.
	@rtype: L{Group}
	@raise ResourceNotFound: If the group does not exist.
	@raise BadRequest: When the RestAuth service returns HTTP status code 400
	@raise InternalServerError: When the RestAuth service returns HTTP status code 500
	"""
	resp = conn.get( '%s%s'%(Group.prefix, name) )
	if resp.status == 204:
		return Group( conn, name )
	elif resp.status == 404:
		raise ResourceNotFound( resp )
	else:
		raise UnknownStatus( resp )

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

	def get_members( self ):
		"""
		Get all members of this group.
		
		@return: A list of L{users<User>}.
		@rtype: list
		@raise ResourceNotFound: If the group does not exist.
		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		"""
		params = {}

		resp = self._get( '/%s/users/'%(self.name), params )
		if resp.status == 200:
			# parse user-list:
			body = resp.read().decode( 'utf-8' )
			names = self.conn.content_handler.unmarshal_list( body )
			users = [ restauth_user.User( self.conn, name ) for name in names ]
			return users
		elif resp.status == 404:
			raise ResourceNotFound( resp )
		else:
			raise UnknownStatus( resp )

	def add_user( self, user ):
		"""
		Add a user to this group.

		@param user: The user to add.
		@type  user: L{user}
		@raise ResourceNotFound: If the group or user does not exist.
		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@todo: It should be possible that user is a str.
		"""
		params = { 'user': user.name }

		resp = self._post( '/%s/users/'%(self.name), params )
		if resp.status == 204:
			return
		elif resp.status == 404:
			raise ResourceNotFound( resp )
		else:
			raise UnknownStatus( resp )

	def add_group( self, group ):
		"""
		Add a group to this group.
		
		@param group: The group to add.
		@type  group: L{Group}
		@raise ResourceNotFound: If the group or user does not exist.
		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@todo: It should be possible that group is a str.
		"""
		path = '/%s/groups/'%(self.name)
		params = { 'group': group.name }
		
		resp = self._post( path, params )
		if resp.status == 204:
			return
		elif resp.status == 404:
			raise ResourceNotFound( resp )
		else:
			raise UnknownStatus( resp )

	def get_groups( self, group ):
		"""
		Get a list of sub-groups of this group.

		@param group: The group to add.
		@type  group: L{Group}
		@raise ResourceNotFound: If the sub- or meta-group not exist.
		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		"""
		path = '/%s/groups/'%(self.name)
		resp = self._get( path )
		if resp.status == 200:
			body = resp.read().decode( 'utf-8' )
			names = self.conn.content_handler.unmarshal_list( body )
			return [ Group( self.conn, name ) for name in names ]
		elif resp.status == 404:
			raise ResourceNotFound( resp )
		else:
			raise UnknownStatus( resp )

	def remove_group( self, group ):
		"""
		Remove a sub-group from this group.
		path = '/%s/groups/%s/'%(self.name, group.name)
		
		@param group: The group to add.
		@type  group: L{Group}
		@raise ResourceNotFound: If the sub- or meta-group not exist.
		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		"""
		path = '/%s/groups/%s/'%(self.name, group.name)
		resp = self._delete( path )
		if resp.status == 204:
			return
		elif resp.status == 404:
			raise ResourceNotFound( resp )
		else:
			raise UnknownStatus( resp )
		
	def remove( self ):
		"""
		Delete this group.
		
		@raise ResourceNotFound: If the group does not exist.
		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		"""
		resp = self._delete( self.name )
		if resp.status == 204:
			return
		elif resp.status == 404:
			raise ResourceNotFound( resp )
		else:
			raise UnknownStatus( resp )

	def is_member( self, user ):
		"""
		Check if the named user is a member.
		
		@param user: The user in question.
		@type  user: L{User}
		@return: True if the user is a member, False if not.
		@rtype: bool

		@raise ResourceNotFound: If the group or user does not exist.
		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@todo: It should be possible that user is a str.
		@todo: this code looks really wrong: a Post to where?
		"""
		path = '/%s/users/%s/'%(self.name, user.name)
		resp = self._get( path )
		if resp.status == 204:
			return True
		elif resp.status == 404:
			if resp.getheader( 'Resource-Type' ) == 'user':
				return False
			else:
				raise ResourceNotFound( resp )
		else:
			raise UnknownStatus( resp )

	def remove_user( self, user ):
		"""
		Remove the given user from the group.

		@raise ResourceNotFound: If the group or user does not exist.
		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		@todo: It should be possible that user is a str.
		"""
		path = '/%s/users/%s/'%(self.name, user.name)
		resp = self._delete( path )
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

	def __repr__( self ):
		import sys
		if sys.version_info < (3, 0) and self.name.__class__ == unicode:
			return '<Group: {0}>'.format(self.name.encode( 'utf-8' ))
		else:
			return '<Group: {0}>'.format(self.name)
			
