# -*- coding: utf-8 -*-
#
# This file is part of RestAuthClient (https://python.restauth.net).
#
# RestAuth is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RestAuth is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RestAuth.  If not, see <http://www.gnu.org/licenses/>.

"""
Module handling code relevant to group handling.

.. moduleauthor:: Mathias Ertl <mati@restauth.net>
"""

import sys
try:
	from RestAuthClient import common, restauth_user
	from RestAuthClient.error import *
except ImportError: # pragma: no cover
	import common, restauth_user
	from error import *
	
try:
	from RestAuthCommon import error
except ImportError: # pragma: no cover
	print( "Error: The RestAuthCommon library is not installed." )
	sys.exit(1)

if sys.version_info < (3, 0):
	import httplib as http
else: # pragma: no cover
	from http import client as http

def create( conn, name ):
	"""
	Factory method that creates a *new* group in RestAuth.

	:param conn: A connection to a RestAuth service.
	:type  conn: :py:class:`.RestAuthConnection`
	:param name: The name of the group to create
	:type  name: str
	:return: The group object representing the group just created.
	:rtype: Group

	:raise BadRequest: If the server was unable to parse the request body.
	:raise Unauthorized: When the connection uses wrong credentials.
	:raise GroupExists: When the user already exists.
	:raise UnsupportedMediaType: The server does not support the
		content type used by this connection (see also: 
		:py:meth:`~.RestAuthConnection.set_content_handler`).
	:raise InternalServerError: When the RestAuth service returns HTTP status code 500
	:raise UnknownStatus: If the response status is unknown.
	"""
	resp = conn.post( Group.prefix, { 'group': name } )
	if resp.status == http.CREATED:
		return Group( conn, name )
	elif resp.status == http.CONFLICT:
		raise GroupExists( "Conflict." )
	elif resp.status == http.PRECONDITION_FAILED:
		raise error.PreconditionFailed( resp )
	else: # pragma: no cover
		raise UnknownStatus( resp )
		
def create_test( conn, name ):
	"""
	Do a test-run on creating a new group (i.e. to test user input against the RestAuth server
	configuration). This method throws the exact same Exceptions as :py:func:`create` but always
	returns None instead of a :py:class:`Group` instance if the group could be created that way.
	
	.. NOTE:: Invoking this method cannot guarantee that actually creating this group
	   will work in the future, i.e. it may have been created by another client in the meantime.
	"""
	resp = conn.post( '/test/%s/'%Group.prefix, { 'group': name } )
	if resp.status == http.CREATED:
		return True
	elif resp.status == http.CONFLICT:
		raise GroupExists( "Conflict." )
	elif resp.status == http.PRECONDITION_FAILED:
		raise error.PreconditionFailed( resp )
	else: # pragma: no cover
		raise UnknownStatus( resp )

def get_all( conn, user=None ):
	"""
	Factory method that gets all groups for this service known to
	RestAuth.

	:param conn: A connection to a RestAuth service.
	:type  conn: :py:class:`.RestAuthConnection`
	:param user: Only return groups where the named user is a member
	:type  user: str
	:return: A list of Group objects
	:rtype: List of :py:class:`groups <.Group>`

	:raise Unauthorized: When the connection uses wrong credentials.
	:raise ResourceNotFound: When the given user does not exist.
	:raise NotAcceptable: When the server cannot generate a response
		in the content type used by this connection (see also:
		:py:meth:`~.RestAuthConnection.set_content_handler`).
	:raise InternalServerError: When the RestAuth service returns HTTP status code 500
	:raise UnknownStatus: If the response status is unknown.
	"""
	params = {}
	if user:
		if user.__class__ == restauth_user.User:
			user = user.name

		params['user'] = user

	resp = conn.get( Group.prefix, params )
	if resp.status == http.OK:
		body = resp.read().decode( 'utf-8' )
		names = conn.content_handler.unmarshal_list( body )
		return [ Group( conn, name ) for name in names ]
	elif resp.status == http.NOT_FOUND:
		raise error.ResourceNotFound( resp )
	else: # pragma: no cover
		raise UnknownStatus( resp )

def get( conn, name ):
	"""
	Factory method that gets an *existing* user from RestAuth. This
	method verifies that the user exists in the RestAuth and throws
	:py:exc:`.ResourceNotFound` if not. 

	:param conn: A connection to a RestAuth service.
	:type  conn: :py:class:`.RestAuthConnection`
	:param name: The name of the group to get
	:type  name: str
	:return: The group object representing the group in RestAuth.
	:rtype: :py:class:`.Group`

	:raise Unauthorized: When the connection uses wrong credentials.
	:raise ResourceNotFound: If the group does not exist.
	:raise InternalServerError: When the RestAuth service returns HTTP status code 500
	:raise UnknownStatus: If the response status is unknown.
	"""
	resp = conn.get( '%s%s'%(Group.prefix, name) )
	if resp.status == http.NO_CONTENT:
		return Group( conn, name )
	elif resp.status == http.NOT_FOUND:
		raise error.ResourceNotFound( resp )
	else: # pragma: no cover
		raise UnknownStatus( resp )

class Group( common.RestAuthResource ):
	"""
	An instance of this class represents a group in RestAuth.

	*Note:* The constructor *does not* verify that the group actually exists.
	This has the advantage of saving one request to the RestAuth service.
	If you want to be sure that a user exists, use :py:func:`get` or
	:py:func:`get_all`.
	
	:param conn: The connection to the RestAuthServer.
	:type  conn: :py:class:`.RestAuthConnection`
	:param name: The name of this user.
	:type  name: str
	"""

	prefix = '/groups/'

	def __init__( self, conn, name ):
		self.conn = conn
		self.name = name

	def get_members( self ):
		"""
		Get all members of this group.
		
		:return: A list of :py:class:`users <.User>`.
		:rtype: list

		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the group does not exist.
		:raise NotAcceptable: When the server cannot generate a response
			in the content type used by this connection (see also:
			:py:meth:`~.RestAuthConnection.set_content_handler`).
		:raise InternalServerError: When the RestAuth service returns HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		params = {}

		resp = self._get( '/%s/users/'%(self.name), params )
		if resp.status == http.OK:
			# parse user-list:
			body = resp.read().decode( 'utf-8' )
			names = self.conn.content_handler.unmarshal_list( body )
			users = [ restauth_user.User( self.conn, name ) for name in names ]
			return users
		elif resp.status == http.NOT_FOUND:
			raise error.ResourceNotFound( resp )
		else: # pragma: no cover
			raise UnknownStatus( resp )

	def add_user( self, user ):
		"""
		Add a user to this group.

		:param user: The user or the name of the user to add.
		:type  user: :py:class:`.User` or str

		:raise BadRequest: If the server was unable to parse the request
			body.
		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the group or user does not exist.
		:raise UnsupportedMediaType: The server does not support the
			content type used by this connection (see also: 
			:py:meth:`~.RestAuthConnection.set_content_handler`).
		:raise InternalServerError: When the RestAuth service returns HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		if user.__class__ == restauth_user.User:
			user = user.name
		params = { 'user': user }
		resp = self._post( '/%s/users/'%(self.name), params )
		if resp.status == http.NO_CONTENT:
			return
		elif resp.status == http.NOT_FOUND:
			raise error.ResourceNotFound( resp )
		else: # pragma: no cover
			raise UnknownStatus( resp )

	def add_group( self, group ):
		"""
		Add a group to this group.
		
		:param group: The group or the name of the group to add.
		:type  group: :py:class:`.Group` or str

		:raise BadRequest: If the server was unable to parse the request
			body.
		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the group or user does not exist.
		:raise UnsupportedMediaType: The server does not support the
			content type used by this connection (see also: 
			:py:meth:`~.RestAuthConnection.set_content_handler`).
		:raise InternalServerError: When the RestAuth service returns HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		if group.__class__ == Group:
			group = group.name
		
		params = { 'group': group }
		path = '/%s/groups/'%(self.name)
		
		resp = self._post( path, params )
		if resp.status == http.NO_CONTENT:
			return
		elif resp.status == http.NOT_FOUND:
			raise error.ResourceNotFound( resp )
		else: # pragma: no cover
			raise UnknownStatus( resp )

	def get_groups( self ):
		"""
		Get a list of sub-groups of this group.

		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the sub- or meta-group not exist.
		:raise NotAcceptable: When the server cannot generate a response
			in the content type used by this connection (see also:
			:py:meth:`~.RestAuthConnection.set_content_handler`).
		:raise InternalServerError: When the RestAuth service returns HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		path = '/%s/groups/'%(self.name)
		resp = self._get( path )
		if resp.status == http.OK:
			body = resp.read().decode( 'utf-8' )
			names = self.conn.content_handler.unmarshal_list( body )
			return [ Group( self.conn, name ) for name in names ]
		elif resp.status == http.NOT_FOUND:
			raise error.ResourceNotFound( resp )
		else: # pragma: no cover
			raise UnknownStatus( resp )

	def remove_group( self, group ):
		"""
		Remove a sub-group from this group.
		
		:param group: The group or the name of the group to remmove.
		:type  group: :py:class:`.Group` or str

		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the sub- or meta-group not exist.
		:raise InternalServerError: When the RestAuth service returns HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		if group.__class__ == Group:
			group = group.name

		path = '/%s/groups/%s/'%(self.name, group)
		resp = self._delete( path )
		if resp.status == http.NO_CONTENT:
			return
		elif resp.status == http.NOT_FOUND:
			raise error.ResourceNotFound( resp )
		else: # pragma: no cover
			raise UnknownStatus( resp )
		
	def remove( self ):
		"""
		Delete this group.
		
		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the group does not exist.
		:raise InternalServerError: When the RestAuth service returns HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		resp = self._delete( self.name )
		if resp.status == http.NO_CONTENT:
			return
		elif resp.status == http.NOT_FOUND:
			raise error.ResourceNotFound( resp )
		else: # pragma: no cover
			raise UnknownStatus( resp )

	def is_member( self, user ):
		"""
		Check if the named user is a member.
		
		:param user: The user or the name of a user in question.
		:type  user: :py:class:`.User` or str
		:return: True if the user is a member, False if not.
		:rtype: bool

		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the group or user does not exist.
		:raise InternalServerError: When the RestAuth service returns HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		if user.__class__ == restauth_user.User:
			user = user.name

		path = '/%s/users/%s/'%(self.name, user)
		resp = self._get( path )
		if resp.status == http.NO_CONTENT:
			return True
		elif resp.status == http.NOT_FOUND:
			if resp.getheader( 'Resource-Type' ) == 'user':
				return False
			else:
				raise error.ResourceNotFound( resp )
		else: # pragma: no cover
			raise UnknownStatus( resp )

	def remove_user( self, user ):
		"""
		Remove the given user from the group.

		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the group or user does not exist.
		:raise InternalServerError: When the RestAuth service returns HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		if user.__class__ == restauth_user.User:
			user = user.name

		path = '/%s/users/%s/'%(self.name, user)
		resp = self._delete( path )
		if resp.status == http.NO_CONTENT:
			return
		elif resp.status == http.NOT_FOUND:
			raise error.ResourceNotFound( resp )
		else: # pragma: no cover
			raise UnknownStatus( resp )

	def __eq__( self, other ):
		"""
		Two instances of the class User evaluate as equal if their name
		and connection evaluate as equal.
		"""
		return self.name == other.name and self.conn == other.conn

	def __repr__( self ): # pragma: no cover
		import sys
		if sys.version_info < (3, 0) and self.name.__class__ == unicode:
			return '<Group: {0}>'.format(self.name.encode( 'utf-8' ))
		else:
			return '<Group: {0}>'.format(self.name)
			
