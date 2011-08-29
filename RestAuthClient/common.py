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
Central code for handling connections to a RestAuth service.

.. moduleauthor:: Mathias Ertl <mati@restauth.net>
"""
try:
	from http import client
except ImportError:
	# this is for python 2.x and earlier
	import httplib as client

import os, sys, base64, time
try:
	from RestAuthClient.error import *
except ImportError:
	from error import *

try:
	from urllib.parse import quote, urlencode, urlparse
except ImportError:
	# this is for python 2.x and earlier
	from urllib import quote, urlencode
	from urlparse import urlparse

try:
	import RestAuthCommon
	from RestAuthCommon import error
except ImportError:
	print( "Error: The RestAuthCommon library is not installed." )
	sys.exit(1)

class RestAuthConnection:
	"""
	An instance of this class represents a connection to a RestAuth service.

	Note that the constructor does not verify that the connection actually
	works. Since HTTP is stateless, there is no way of knowing if a
	connection working now will still work 0.2 seconds from now. 		
	
	:param host: The hostname of the RestAuth service
	:type  host: str
	:param host: The hostname of the RestAuth service
	:type  host: str
	:param user: The service name to use for authenticating with 
		RestAuth (passed to :py:meth:`.set_credentials`).
	:type  user: str
	:param passwd: The password to use for authenticating with
		RestAuth (passed to :py:meth:`.set_credentials`).
	:type  passwd: str
	:param content_handler: Directly passed to :py:meth:`.set_content_handler`}.
	:type  content_handler: str or subclass of 
		RestAuthCommon.handlers.content_handler.
	"""
	
	def __init__( self, host, user, passwd, content_handler='application/json' ):
		"""
		Initialize a new connection to a RestAuth service. 
		

		"""
		parseresult = urlparse( host )
		if parseresult.scheme == 'https':
			self.use_ssl = True
		else:
			self.use_ssl = False
		self.host = parseresult.netloc

		self.user = user
		self.passwd = passwd
		self.set_content_handler( content_handler )
	
		# pre-calculate the auth-header so we only have to do this once:
		self.set_credentials( user, passwd )

	def set_credentials( self, user, passwd ):
		"""
		Set the password for the given user. This method is also
		automatically called by the constructor.

		:param user: The user for whom the password should be changed.
		:type  user: str
		:param passwd: The password to use
		:type  passwd: str
		"""
		raw_credentials = '%s:%s'%( user, passwd )
		enc_credentials = base64.b64encode( raw_credentials.encode() )
		self.auth_header = "Basic %s"%(enc_credentials.decode() )

	def set_content_handler( self, content_handler='application/json' ):
		"""
		Set the content type used by this connection. The default value
		is 'json', which is supported by the reference server
		implementation.

		:param content_handler: Either a self-implemented handler, which
			must be a subclass of
			RestAuthCommon.handlers.content_handler or a str
			str, in which case the str suffixed with '_handler'
			must give a class found in RestAuthCommon.handlers.
		:type  content_handler: str or 
			RestAuthCommon.handlers.content_handler.

		"""
		if isinstance( content_handler, RestAuthCommon.handlers.content_handler ):
			self.content_handler = content_handler
		elif isinstance( content_handler, str ):
			handler_dict = RestAuthCommon.CONTENT_HANDLERS
			try:
				cl = handler_dict[content_handler]
			except KeyError:
				raise RuntimeError( "Unknown content_handler: %s"%(content_handler) )
			
			self.content_handler = cl()

	def send( self, method, url, body=None, headers={} ):
		"""
		Send an HTTP request to the RestAuth service. This method is
		called by the :py:meth:`.get`, :py:meth:`.post`, :py:meth:`.put`
		and :py:meth:`.delete` methods. This method takes care of
		service authentication, encryption and sets Content-Type and
		Accept headers.
		:py:class:`http.client.HTTPResponse`

		:param method: The HTTP method to use. Must be either "GET",
			"POST", "PUT" or "DELETE".
		:type  method: str
		:param    url: The URL path of the request. This does not
			include the domain, which is configured by the 
			:py:class:`constructor <.RestAuthConnection>`.
			The path is assumed to be URL escaped.
		:type     url: str
		:param   body: The request body. This (should) only be used by
			POST and PUT requests. The body is assumed to be URL
			escaped.
		:type    body: str
		:param headers: A dictionary of key/value pairs of headers to set.
		:param headers: dict

		:return: The response to the request
		:rtype: :py:class:`http.client.HTTPResponse`

		:raise Unauthorized: When the connection uses wrong credentials.
		:raise NotAcceptable: When the server cannot generate a response
			in the content type used by this connection (see also:
			:py:meth:`.set_content_handler`).
		:raise InternalServerError: When the server has some internal
			error.
		"""
		headers['Authorization'] = self.auth_header
		headers['Accept'] = self.content_handler.mime
	
		if self.use_ssl:
			conn = client.HTTPSConnection( self.host )
		else:
			conn = client.HTTPConnection( self.host )

		try:
			conn.request( method, url, body, headers )
			response = conn.getresponse()
		except Exception as e:
			raise HttpException( e )

		if response.status == client.UNAUTHORIZED:
			raise error.Unauthorized( response )
		elif response.status == client.NOT_ACCEPTABLE:
			raise error.NotAcceptable( response )
		elif response.status == client.INTERNAL_SERVER_ERROR:
			raise error.InternalServerError( response )
		else:
			return response

	def _sanitize_qs( self, params ):
		"""
		@todo: replace still necessary?
		"""
		if sys.version_info < (3, 0):
			for key, value in params.iteritems():
				if key.__class__ == unicode:
					key = key.encode( 'utf-8' )
				if value.__class__ == unicode:
					value = value.encode( 'utf-8' )
				params[key] = value

		return urlencode( params ).replace( '+', '%20' )
		
	def _sanitize_url( self, url ):
		# make sure that it starts and ends with /, cut double-slashes:
		url = '%s/'%( os.path.normpath( url ) )
		if not url.startswith( '/' ):
			url = '/%s'%(url)

		if sys.version_info < (3, 0) and url.__class__ == unicode: 
			url = url.encode( 'utf-8' ) # encode utf-8 in python 2.x

		url = quote( url )
		return url

	def get( self, url, params={}, headers={} ):
		"""
		Perform a GET request on the connection. This method takes care
		of escaping parameters and assembling the correct URL. This
		method internally calls the :py:meth:`.send` function to perform service
		authentication.

		:param url: The URL to perform the GET request on. The URL
			must not include a query string.
		:type  url: str
		:param params: The query parameters for this request. A
			dictionary of key/value pairs that is passed to
			:py:func:`urllib.parse.quote`.
		:type  params: dict
		:param headers: Additional headers to send with this request.
		:type  headers: dict
		
		:return: The response to the request
		:rtype: :py:class:`http.client.HTTPResponse`

		:raise Unauthorized: When the connection uses wrong credentials.
		:raise NotAcceptable: When the server cannot generate a response
			in the content type used by this connection (see also:
			:py:meth:`.set_content_handler`).
		:raise InternalServerError: When the server has some internal
			error.
		"""
		url = self._sanitize_url( url )
		if params:
			url = '%s?%s'%( url, self._sanitize_qs( params ) )

		return self.send( 'GET', url, headers=headers )

	def post( self, url, params={}, headers={} ):
		"""
		Perform a POST request on the connection. This method takes care
		of escaping parameters and assembling the correct URL. This
		method internally calls the :py:meth:`.send` function to perform service
		authentication.

		:param url: The URL to perform the GET request on. The URL
			must not include a query string.
		:type  url: str
		:param params: A dictionary that will be wrapped into the
			request body.
		:type  params: dict
		:param headers: Additional headers to send with this request.
		:type  headers: dict

		:return: The response to the request
		:rtype: :py:class:`http.client.HTTPResponse`

		:raise BadRequest: If the server was unable to parse the request
			body.
		:raise Unauthorized: When the connection uses wrong credentials.
		:raise NotAcceptable: When the server cannot generate a response
			in the content type used by this connection (see also:
			:py:meth:`.set_content_handler`).
		:raise UnsupportedMediaType: The server does not support the
			content type used by this connection.
		:raise InternalServerError: When the server has some internal
			error.
		"""
		headers['Content-Type'] = self.content_handler.mime
		body = self.content_handler.marshal_dict( params )
		url = self._sanitize_url( url )
		response = self.send( 'POST', url, body, headers )
		if response.status == client.BAD_REQUEST:
			raise error.BadRequest( response )
		elif response.status == client.UNSUPPORTED_MEDIA_TYPE:
			raise error.UnsupportedMediaType( response )

		return response

	def put( self, url, params={}, headers={} ):
		"""
		Perform a PUT request on the connection. This method takes care
		of escaping parameters and assembling the correct URL. This
		method internally calls the :py:meth:`.send`} function to perform service
		authentication.

		:param url: The URL to perform the GET request on. The URL
			must not include a query string.
		:type  url: str
		:param params: A dictionary that will be wrapped into the
			request body.
		:type  params: dict
		:param headers: Additional headers to send with this request.
		:type  headers: dict

		:return: The response to the request
		:rtype: :py:class:`http.client.HTTPResponse`

		:raise BadRequest: If the server was unable to parse the request
			body.
		:raise Unauthorized: When the connection uses wrong credentials.
		:raise NotAcceptable: When the server cannot generate a response
			in the content type used by this connection (see also:
			:py:meth:`.set_content_handler`).
		:raise UnsupportedMediaType: The server does not support the
			content type used by this connection.
		:raise InternalServerError: When the server has some internal
			error.
		"""
		headers['Content-Type'] = self.content_handler.mime
		body = self.content_handler.marshal_dict( params )
		url = self._sanitize_url( url )
		response = self.send( 'PUT', url, body, headers )
		if response.status == client.BAD_REQUEST:
			raise error.BadRequest( response )
		elif response.status == client.UNSUPPORTED_MEDIA_TYPE:
			raise error.UnsupportedMediaType( response )
		return response

	def delete( self, url, headers={} ):
		"""
		Perform a GET request on the connection. This method internally
		calls the :py:meth:`.send` function to perform service authentication.

		:param url: The URL to perform the GET request on. The URL must
			not include a query string.
		:type  url: str
		:param headers: Additional headers to send with this request.
		:type  headers: dict
		:return: The response to the request
		:rtype: :py:class:`httplib.HTTPResponse`
		:raise Unauthorized: When the connection uses wrong credentials.
		:raise NotAcceptable: When the server cannot generate a response
			in the content type used by this connection (see also: 
			:py:meth:`.set_content_handler` ).
		:raise InternalServerError: When the server has some internal error.
		"""
		url = self._sanitize_url( url )
		return self.send( 'DELETE', url, headers=headers )
	
	def __eq__( self, other ):
		return self.host == other.host and self.user == other.user and \
			self.passwd == other.passwd

class RestAuthResource:
	"""
	Superclass for :py:class:`~.User` and :py:class:`~.Group` objects.
	The private methods of this class do nothing but prefix all request URLs
	with the prefix of that class (i.e. /users/).
	"""

	def _get( self, url, params={}, headers={} ):
		"""
		Internal method that prefixes a GET request with the resource
		name and passes the request to :py:meth:`RestAuthConnection.get`.
		"""
		url = '%s%s'%( self.__class__.prefix, url )
		return self.conn.get( url, params, headers )
	
	def _post( self, url, params={}, headers={} ):
		"""
		Internal method that prefixes a POST request with the resources
		name and passes the request to :py:meth:`RestAuthConnection.post`.
		
		"""
		url = '%s%s'%( self.__class__.prefix, url )
		return self.conn.post( url, params, headers )
	
	def _put( self, url, params={}, headers={} ):
		"""
		Internal method that prefixes a PUT request with the resources
		name and passes the request to :py:meth:`RestAuthConnection.put`.
		
		"""
		url = '%s%s'%( self.__class__.prefix, url )
		return self.conn.put( url, params, headers )
	
	def _delete( self, url, headers={} ):
		"""
		Internal method that prefixes a DELETE request with the
		resources name and passes the request to :py:meth:`RestAuthConnection.delete`.
		
		"""
		url = '%s%s'%( self.__class__.prefix, url )
		return self.conn.delete( url, headers )

