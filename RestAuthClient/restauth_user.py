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
Module handling code relevant to user authentication and property management.
"""

import sys
try:
	from RestAuthClient import common
	from RestAuthClient.error import *
except ImportError: # pragma: no cover
	from error import *
	import common
	
try:
	from RestAuthCommon import error
except ImportError: # pragma: no cover
	print( "Error: The RestAuthCommon library is not installed." )
	sys.exit(1)

if sys.version_info < (3, 0):
	import httplib as http
else: # pragma: no cover
	from http import client as http

def create( conn, name, password=None, properties=None ):
	"""
	Factory method that creates a *new* user in the RestAuth
	database.
	
	:param conn: A connection to a RestAuth service.
	:type  conn: :py:class:`.RestAuthConnection`
	:param name: Name of the user to get
	:type  name: str
	:param password: Password for the new user. If None or an empty string, the user is effectively
		disabled.
	:type  password: str
	:return: The user object representing the user just created.
	:rtype: :py:class:`~.restauth_user.User`

	:raise BadRequest: If the server was unable to parse the request body.
	:raise Unauthorized: When the connection uses wrong credentials.
	:raise UserExists: If the user already exists.
	:raise PreconditionFailed: When username or password is invalid.
	:raise UnsupportedMediaType: The server does not support the
		content type used by this connection (see also: 
		:py:meth:`~.RestAuthConnection.set_content_handler`).
	:raise InternalServerError: When the RestAuth service returns HTTP
		status code 500
	:raise UnknownStatus: If the response status is unknown.
	"""
	params = { 'user': name }
	if password:
		params['password'] = password
	if properties:
		params['properties'] = properties
		
	resp = conn.post( User.prefix, params )
	if resp.status == http.CREATED:
		return User( conn, name )
	elif resp.status == http.CONFLICT:
		raise UserExists( name )
	elif resp.status == http.PRECONDITION_FAILED:
		raise error.PreconditionFailed( resp.read() )
	else: # pragma: no cover
		raise UnknownStatus( resp )
		
def create_test( conn, name, password=None, properties=None ):
	"""
	Do a test-run on creating a new user (i.e. to test user input against the RestAuth server
	configuration). This method throws the exact same Exceptions as :py:func:`create` but always
	returns None instead of a :py:class:`User` instance if the user could be created that way.
	
	.. NOTE:: Invoking this method cannot guarantee that actually creating this user
	   will work in the future, i.e. it may have been created by another client in the meantime.
	"""
	params = { 'user': name }
	if password:
		params['password'] = password
	if properties:
		params['properties'] = properties
		
	resp = conn.post( '/test/%s/'%User.prefix, params )
	if resp.status == http.CREATED:
		return
	elif resp.status == http.CONFLICT:
		raise UserExists( name )
	elif resp.status == http.PRECONDITION_FAILED:
		raise error.PreconditionFailed( resp )
	else: # pragma: no cover
		raise UnknownStatus( resp )

def get( conn, name ):
	"""
	Factory method that gets an *existing* user from RestAuth. This
	method verifies that the user exists in RestAuth and throws
	:py:exc:`~RestAuthCommon:RestAuthCommon.error.ResourceNotFound` if not.

	:param conn: A connection to a RestAuth service.
	:type  conn: :py:class:`.RestAuthConnection`
	:param name: Name of the user to get
	:type  name: str
	:return: The user object representing the user just created.
	:rtype: :py:class:`~.restauth_user.User`

	:raise Unauthorized: When the connection uses wrong credentials.
	:raise ResourceNotFound: If the user does not exist in RestAuth.
	:raise InternalServerError: When the RestAuth service returns
		HTTP status code 500
	:raise UnknownStatus: If the response status is unknown.
	"""
	# this just verify that the user exists in RestAuth:
	resp = conn.get( '/users/%s/'%(name) )

	if resp.status == http.NO_CONTENT:
		return User( conn, name )
	elif resp.status == http.NOT_FOUND:
		raise error.ResourceNotFound( resp )
	else: # pragma: no cover
		raise UnknownStatus( resp )
	
def get_all( conn ):
	"""
	Factory method that gets all users known to RestAuth.

	:param conn: A connection to a RestAuth service.
	:type  conn: :py:class:`.RestAuthConnection`
	:return: A list of User objects
	:rtype: [:py:class:`~.restauth_user.User`]

	:raise Unauthorized: When the connection uses wrong credentials.
	:raise NotAcceptable: When the server cannot generate a response in the
		content type used by this connection (see also: 
		:py:meth:`~.RestAuthConnection.set_content_handler`).
	:raise InternalServerError: When the RestAuth service returns HTTP
		status code 500
	:raise UnknownStatus: If the response status is unknown.
	"""
	resp = conn.get( User.prefix )
		
	if resp.status == http.OK:
		body = resp.read().decode( 'utf-8' )
		usernames = conn.content_handler.unmarshal_list( body )
		return [ User( conn, name ) for name in usernames ]
	else: # pragma: no cover
		raise UnknownStatus( resp )

class User( common.RestAuthResource ):
	"""
	An instance of this class is an object oriented abstraction of a user in a RestAuth server.

	.. Warning:: The constructor *does not* verify that the user actually exists.
	   This has the advantage of saving one request to the RestAuth service.
	   If you want to be sure that a user exists, use :py:meth:`~.restauth_user.get` or
	   :py:meth:`~.restauth_user.get_all`.

	:param conn: The connection to the RestAuthServer.
	:type  conn: :py:class:`.RestAuthConnection`
	:param name: The name of this user.
	:type  name: str
	"""
	prefix = '/users/' #: Prefix used for HTTP query methods inherited from base class

	def __init__( self, conn, name ):
		self.conn = conn
		self.name = name

	def set_password( self, password=None ):
		"""
		Set the password of this user.
		
		:param password: The new password of the user. If None or an empty string, the
			user is effectively disabled.
		:type  password: str

		:raise BadRequest: If the server was unable to parse the request
			body.
		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the user does not exist in RestAuth.
		:raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		:raise UnsupportedMediaType: The server does not support the
			content type used by this connection (see also: 
			:py:meth:`~.RestAuthConnection.set_content_handler`).
		:raise UnknownStatus: If the response status is unknown.
		:raise PreconditionFailed: When the password is invalid.
		"""
		params = {}
		if password:
			params['password'] = password
		resp = self._put( self.name, params )
		if resp.status == http.NO_CONTENT:
			return
		elif resp.status == http.NOT_FOUND:
			raise error.ResourceNotFound( resp )
		elif resp.status == http.PRECONDITION_FAILED:
			raise error.PreconditionFailed( resp.read() )
		else: # pragma: no cover
			raise UnknownStatus( resp )

	def verify_password( self, password ):
		"""
		Verify the given password.

		:param password: The password to verify.
		:type  password: str
		:return: True if the password is correct, False if the password
			is wrong or the user does not exist.
		:rtype: bool

		:raise BadRequest: If the server was unable to parse the request
			body.
		:raise Unauthorized: When the connection uses wrong credentials.
		:raise UnsupportedMediaType: The server does not support the
			content type used by this connection (see also: 
			:py:meth:`~.RestAuthConnection.set_content_handler`).
		:raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		resp = self._post( self.name, { 'password': password } )
		if resp.status == http.NO_CONTENT:
			return True
		elif resp.status == http.NOT_FOUND:
			return False
		else: # pragma: no cover
			raise UnknownStatus( resp )

	def remove( self ):
		"""
		Remove this user.

		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the user does not exist in RestAuth.
		:raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		resp = self._delete( self.name )
		if resp.status == http.NO_CONTENT:
			return
		if resp.status == http.NOT_FOUND:
			raise error.ResourceNotFound( resp )
		else: # pragma: no cover
			raise UnknownStatus( resp )

	def get_properties( self ):
		"""
		Get all properties defined for this user.

		:return: A key/value array of the properties defined for this user.
		:rtype: dict

		:raise Unauthorized: When the connection uses wrong credentials.
		:raise NotAcceptable: When the server cannot generate a response
			in the content type used by this connection (see also: 
			:py:meth:`~.RestAuthConnection.set_content_handler`).
		:raise ResourceNotFound: If the user does not exist in RestAuth.
		:raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		resp = self._get( '%s/props/'%(self.name) )
		if resp.status == http.OK:
			body = resp.read().decode( 'utf-8' )
			return self.conn.content_handler.unmarshal_dict( body )
		elif resp.status == http.NOT_FOUND:
			raise error.ResourceNotFound( resp )
		else: # pragma: no cover
			raise UnknownStatus( resp )

	def create_property( self, prop, value ):
		"""
		Create a new property for this user. This method fails if the
		property already exists. Use :py:meth:`set_property` if you do
		not care if the property already exists.

		:param prop: The property to set.
		:type  prop: str
		:param value: The new value of the property
		:type  value: str

		:raise BadRequest: If the server was unable to parse the request
			body.
		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the user does not exist in RestAuth.
		:raise PropertyExists: When the property already exists
		:raise PreconditionFailed: When the propertyname contains invalid characters
		:raise UnsupportedMediaType: The server does not support the
			content type used by this connection (see also: 
			:py:meth:`~.RestAuthConnection.set_content_handler`).
		:raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		params = { 'prop': prop, 'value': value }
		resp = self._post( '%s/props/'%(self.name), params=params )
		if resp.status == http.CREATED:
			return
		elif resp.status == http.NOT_FOUND:
			raise error.ResourceNotFound( resp )
		elif resp.status == http.PRECONDITION_FAILED:
			raise error.PreconditionFailed( resp )
		elif resp.status == http.CONFLICT:
			raise PropertyExists( resp )
		else: # pragma: no cover
			raise UnknownStatus( resp )
			
	def create_property_test( self, prop, value ):
		"""
		Do a test-run on creating a property (i.e. to test user input against the RestAuth
		server configuration). This method throws the exact same Exceptions as
		:py:func:`create_property` and also returns None if creating the property would
		succeed.
		
		.. NOTE:: Invoking this method cannot guarantee that actually creating this
		   property will work in the future, i.e. it may have been created by another client
		   in the meantime.
		"""
		params = { 'prop': prop, 'value': value }
		resp = self.conn.post( '/test/users/%s/props/'%(self.name), params=params )
		
		if resp.status == http.CREATED:
			return
		elif resp.status == http.NOT_FOUND:
			raise error.ResourceNotFound( resp )
		elif resp.status == http.PRECONDITION_FAILED:
			raise error.PreconditionFailed( resp )
		elif resp.status == http.CONFLICT:
			raise PropertyExists( resp )
		else: # pragma: no cover
			raise UnknownStatus( resp )

	def set_property( self, prop, value ):
		"""
		Set a property for this user. This method overwrites any
		previous entry.

		:param prop: The property to set.
		:type  prop: str
		:param value: The new value of the property
		:type  value: str

		:raise BadRequest: If the server was unable to parse the request
			body.
		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the user does not exist in RestAuth.
		:raise NotAcceptable: When the server cannot generate a response
			in the content type used by this connection (see also: 
			:py:meth:`~.RestAuthConnection.set_content_handler`).
		:raise UnsupportedMediaType: The server does not support the
			content type used by this connection (see also: 
			:py:meth:`~.RestAuthConnection.set_content_handler`).
		:raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		url = '%s/props/%s/'%( self.name, prop )
		resp = self._put( url, params={'value': value} )
		if resp.status == http.OK:
			body = resp.read().decode( 'utf-8' )
			return self.conn.content_handler.unmarshal_str( body )
		if resp.status == http.CREATED:
			return
		elif resp.status == http.NOT_FOUND:
			raise error.ResourceNotFound( resp )
		else: # pragma: no cover
			raise UnknownStatus( resp )

	def get_property( self, prop ):
		"""
		Get the given property for this user.

		:return: The value of the property.
		:rtype: str

		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the user or property does not exist.
		:raise NotAcceptable: When the server cannot generate a response
			in the content type used by this connection (see also: 
			:py:meth:`~.RestAuthConnection.set_content_handler`).
		:raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		resp = self._get( '%s/props/%s'%( self.name, prop ) )
		if resp.status == http.OK:
			body = resp.read().decode( 'utf-8' )
			return self.conn.content_handler.unmarshal_str( body )
		elif resp.status == http.NOT_FOUND:
			raise error.ResourceNotFound( resp )
		else: # pragma: no cover
			raise UnknownStatus( resp )

	def remove_property( self, prop ):
		"""
		Delete the given property.

		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the user or property does not exist.
		:raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		resp = self._delete( '%s/props/%s'%(self.name, prop) )
		if resp.status == http.NO_CONTENT:
			return
		elif resp.status == http.NOT_FOUND:
			raise error.ResourceNotFound( resp )
		else: # pragma: no cover
			raise UnknownStatus( resp )

	def get_groups( self ):
		"""
		Get all groups that this user is a member of.
	
		This method is just a shortcut for :py:func:`.group.get_all`.

		:return: All groups that the user is a member of.
		:rtype: list of :py:class:`groups <.Group>`

		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the user does not exist.
		:raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		try:
			from RestAuthClient import group
		except ImportError: # pragma: no cover
			import group
		return group.get_all( self.conn, self )

	def in_group( self, grp ):
		"""
		Check if the user is a member in the given group.

		This method is just a shortcut for :py:meth:`.Group.is_member`.

		:param grp: The group of interest.
		:type  grp: :py:class:`str` or :py:class:`.Group`
		:return: True if this user is a member, False otherwise.
		:rtype: bool
		
		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the user or group does not exist.
		:raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		try:
			from RestAuthClient import group
		except ImportError: # pragma: no cover
			import group
		if grp.__class__ == str or (sys.version_info < (3, 0) and grp.__class__ == unicode):
			grp = group.Group( self.conn, grp )
		return grp.is_member( self.name )

	def add_group( self, grp ):
		"""
		Make this user a member if the given group.

		This method is just a shortcut for :py:meth:`.Group.add_user`.
		
		:param grp: The group of interest.
		:type  grp: :py:class:`str` or :py:class:`.Group`
		
		:raise BadRequest: If the server was unable to parse the request
			body.
		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the user or group does not exist.
		:raise InternalServerError: When the RestAuth server returns
			HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		try:
			from RestAuthClient import group
		except ImportError: # pragma: no cover
			import group
		if grp.__class__ == str or (sys.version_info < (3, 0) and grp.__class__ == unicode):
			grp = group.Group( self.conn, grp )
		grp.add_user( self.name )

	def remove_group( self, grp ):
		"""
		Remove the users membership from the given group.

		This method is just a shortcut for :py:meth:`.Group.remove_user`.

		:param grp: The group of interest.
		:type  grp: :py:class:`str` or :py:class:`.Group`
		
		:raise Unauthorized: When the connection uses wrong credentials.
		:raise ResourceNotFound: If the user or group does not exist.
		:raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		:raise UnknownStatus: If the response status is unknown.
		"""
		try:
			from RestAuthClient import group
		except ImportError: # pragma: no cover
			import group
		if grp.__class__ == str or (sys.version_info < (3, 0) and grp.__class__ == unicode):
			grp = group.Group( self.conn, grp )
		grp.remove_user( self.name )


	def __eq__( self, other ):
		"""
		Two instances of the class User evaluate as equal if their name
		and connection evaluate as equal.
		"""
		return self.name == other.name and self.conn == other.conn

	def __lt__( self, other ):
		return self.name < other.name
	
	def __hash__( self ): # pragma: no cover
		return hash( self.name )

	def __repr__( self ): # pragma: no cover
		if sys.version_info < (3, 0) and self.name.__class__ == unicode:
			return '<User: {0}>'.format(self.name.encode( 'utf-8' ))
		else:
			return '<User: {0}>'.format( self.name )
