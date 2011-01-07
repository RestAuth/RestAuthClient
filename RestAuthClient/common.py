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
Central code for handling connections to a RestAuth service.
"""
try:
	from http import client
except ImportError:
	# this is for python 2.x and earlier
	import httplib as client

import os, sys, base64, time
try:
	from RestAuthClient.errors import *
except ImportError:
	from errors import *

try:
	from urllib.parse import quote, urlencode, urlparse
except ImportError:
	# this is for python 2.x and earlier
	from urllib import quote, urlencode
	from urlparse import urlparse

try:
	import RestAuthCommon
except ImportError:
	print( "Error: The RestAuthCommon library is not installed." )
	sys.exit(1)

class RestAuthCookie:
	def __init__( self, raw_value ):
		self.creation = time.time()
		self.items = {}

		items = raw_value.split( ';' )
		items = [ item.strip() for item in items ]

		# parse key/value pairs:
		for item in items:
			key, value = item.split( '=', 1 )
			self.items[key.strip().lower()] = value.strip()
		
		if 'expires' in self.items:
			try:
				raw = self.items['expires']
				self.items['expires'] = time.mktime(
					time.strptime( raw, '%a, %d-%b-%Y %H:%M:%S %Z' ) )
			except Exception:
				pass # don't fail on this

		if 'max-age' in self.items:
			try:
				val = int( self.items['max-age'] )
				self.items['expires'] = self.creation + raw
			except Exception:
				pass # don't fail on this
	
	def valid( self ):
		if not 'sessionid' in self.items:
			return False # no sessionid

		if 'expires' in self.items and self.items['expires'] < time.time():
			return False # cookie has expired

		return True

	def get_value( self ):
		return 'sessionid=%s'%(self.items['sessionid'])

	def get_session( self ):
		return self.items['sessionid']

class RestAuthConnection:
	"""
	An instance of this class represents a connection to a RestAuth service.
	"""
	
	def __init__( self, host, user, passwd, use_cookies=True, content_handler='application/json' ):
		"""
		Initialize a new connection to a RestAuth service. 
		
		Note that the constructor does not verify that the connection
		actually works. Since HTTP is stateless, there is no way of
		knowing if a connection working now will still work 0.2 seconds
		from now. 		

		@param host: The hostname of the RestAuth service
		@type  host: str
		@param user: The service name to use for authenticating with 
			RestAuth (passed to L{set_credentials}).
		@type  user: str
		@param passwd: The password to use for authenticating with
			RestAuth (passed to L{set_credentials}).
		@type  passwd: str
		@param use_cookies: Wether or not to use cookies. Using cookies
			is faster when doing multiple requests, but may not work
			on all server configurations.
		@type  use_cookies: bool
		@param content_handler: Directly passed to L{set_content_handler}.
		@type  content_handler: str or subclass of 
			RestAuthCommon.handlers.content_handler.
		"""
		self.cookie = None
		self.use_cookies = use_cookies

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

		@param user: The user for whom the password should be changed.
		@type  user: str
		@param passwd: The password to use
		@type  passwd: str
		"""
		if user and passwd:
			raw_credentials = '%s:%s'%( user, passwd )
			enc_credentials = base64.b64encode( raw_credentials.encode( 'utf-8' ) )
			self.auth_header = "Basic %s"%(enc_credentials.decode( 'ascii' ) )
		else:
			self.auth_header = None

	def set_content_handler( self, content_handler='application/json' ):
		"""
		Set the content type used by this connection. The default value
		is 'json', which is supported by the reference server
		implementation.

		@param content_handler: Either a self-implemented handler, which
			must be a subclass of
			RestAuthCommon.handlers.content_handler or a str
			str, in which case the str suffixed with '_handler'
			must give a class found in RestAuthCommon.handlers.
		@type  content_handler: str or subclass of 
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
		called by the L{get}, L{post}, L{put} and L{delete} methods. 
		This method takes care of service authentication, encryption
		and sets Content-Type and Accept headers.

		@param method: The HTTP method to use. Must be either "GET",
			"POST", "PUT" or "DELETE".
		@type  method: str
		@param    url: The URL to request. This does not include the
			URL, which is passed by the L{constructor<__init__>}.
			The url is assumed to be URL escaped.
		@type     url: str
		@param   body: The request body. This (should) only be used by
			POST and PUT requests. The body is assumed to be URL
			escaped.
		@type    body: str
		@param headers: A dictionary of key/value pairs of headers to set.
		@param headers: dict

		@return: The response to the request
		@rtype: U{HTTPResponse<http://docs.python.org/py3k/library/http.client.html#httpresponse-objects>}

		@raise Unauthorized: When the connection uses wrong credentials.
		@raise NotAcceptable: When the server cannot generate a response
			in the content type used by this connection (see also:
			L{set_content_handler}).
		@raise InternalServerError: When the server has some internal
			error.
		"""
		if self.use_cookies and self.cookie and self.cookie.valid():
			headers['Cookie'] = self.cookie.get_value()
		elif self.auth_header:
			headers['Authorization'] = self.auth_header

		headers['Accept'] = self.content_handler.mime
	
		if self.use_ssl:
			conn = client.HTTPSConnection( self.host )
		else:
			conn = client.HTTPConnection( self.host )

		conn.request( method, url, body, headers )
		response = conn.getresponse()

		# handle cookie:
		try:
			raw_header = response.getheader( 'Set-Cookie', None )
		except TypeError:
			raw_header = None
		if raw_header and (not self.cookie or not self.cookie.valid()):
			self.cookie = RestAuthCookie( raw_header )

		if response.status == 401:
			raise Unauthorized( response )
		elif response.status == 406:
			raise NotAcceptable( response )
		elif response.status == 500:
			body = response.read()
			print( body.decode('utf-8').replace( '\n', "\n") )
			raise InternalServerError( response )
		else:
			return response

	def _sanitize_qs( self, params ):
		"""
		@todo: replace still necessary?
		"""
		return urlencode( params ).replace( '+', '%20' )
		
	def _sanitize_url( self, url ):
		# make sure that it starts and ends with /, cut double-slashes:
		url = '%s/'%( os.path.normpath( url ) )
		if not url.startswith( '/' ):
			url = '/%s'%(url)
		url = quote( url )
		return url

	def get( self, url, params={}, headers={} ):
		"""
		Perform a GET request on the connection. This method takes care
		of escaping parameters and assembling the correct URL. This
		method internally calls the L{send} function to perform service
		authentication.

		@param url: The URL to perform the GET request on. The URL
			must not include a query string.
		@type  url: str
		@param params: The query parameters for this request. A
			dictionary of key/value pairs that is passed to
			U{quote<http://docs.python.org/py3k/library/urllib.parse.html#urllib.parse.quote>}.
		@type  params: dict
		@param headers: Additional headers to send with this request.
		@type  headers: dict
		
		@return: The response to the request
		@rtype: U{HTTPResponse<http://docs.python.org/py3k/library/http.client.html#httpresponse-objects>}

		@raise Unauthorized: When the connection uses wrong credentials.
		@raise NotAcceptable: When the server cannot generate a response
			in the content type used by this connection (see also:
			L{set_content_handler}).
		@raise InternalServerError: When the server has some internal
			error.
		"""
		url = self._sanitize_url( url )
		qs = self._sanitize_qs( params )
		if qs:
			url = '%s?%s'%( url, qs )

		return self.send( 'GET', url, headers=headers )

	def post( self, url, params={}, headers={} ):
		"""
		Perform a POST request on the connection. This method takes care
		of escaping parameters and assembling the correct URL. This
		method internally calls the L{send} function to perform service
		authentication.

		@param url: The URL to perform the GET request on. The URL
			must not include a query string.
		@type  url: str
		@param params: A dictionary that will be wrapped into the
			request body.
		@type  params: dict
		@param headers: Additional headers to send with this request.
		@type  headers: dict

		@return: The response to the request
		@rtype: U{HTTPResponse<http://docs.python.org/py3k/library/http.client.html#httpresponse-objects>}

		@raise BadRequest: If the server was unable to parse the request
			body.
		@raise Unauthorized: When the connection uses wrong credentials.
		@raise NotAcceptable: When the server cannot generate a response
			in the content type used by this connection (see also:
			L{set_content_handler}).
		@raise UnsupportedMediaType: The server does not support the
			content type used by this connection.
		@raise InternalServerError: When the server has some internal
			error.
		"""
		headers['Content-Type'] = self.content_handler.mime
		body = self.content_handler.marshal_dict( params )
		url = self._sanitize_url( url )
		response = self.send( 'POST', url, body, headers )
		if response.status == 400:
			raise BadRequest( response )
		elif response.status == 411:
			raise RuntimeError( "Request did not send a Content-Length header!" )
		elif response.status == 415:
			raise UnsupportedMediaType( response )

		return response

	def put( self, url, params={}, headers={} ):
		"""
		Perform a PUT request on the connection. This method takes care
		of escaping parameters and assembling the correct URL. This
		method internally calls the L{send} function to perform service
		authentication.

		@param url: The URL to perform the GET request on. The URL
			must not include a query string.
		@type  url: str
		@param params: A dictionary that will be wrapped into the
			request body.
		@type  params: dict
		@param headers: Additional headers to send with this request.
		@type  headers: dict

		@return: The response to the request
		@rtype: U{HTTPResponse<http://docs.python.org/py3k/library/http.client.html#httpresponse-objects>}

		@raise BadRequest: If the server was unable to parse the request
			body.
		@raise Unauthorized: When the connection uses wrong credentials.
		@raise NotAcceptable: When the server cannot generate a response
			in the content type used by this connection (see also:
			L{set_content_handler}).
		@raise UnsupportedMediaType: The server does not support the
			content type used by this connection.
		@raise InternalServerError: When the server has some internal
			error.
		"""
		headers['Content-Type'] = self.content_handler.mime
		body = self.content_handler.marshal_dict( params )
		url = self._sanitize_url( url )
		response = self.send( 'PUT', url, body, headers )
		if response.status == 400:
			raise BadRequest( response )
		elif response.status == 411:
			raise RuntimeError( "Request did not send a Content-Length header!" )
		elif response.status == 415:
			raise UnsupportedMediaType( response )
		return response

	def delete( self, url, headers={} ):
		"""
		Perform a GET request on the connection. This method internally
		calls the L{send} function to perform service authentication.

		@param url: The URL to perform the GET request on. The URL
			must not include a query string.
		@type  url: str
		@param headers: Additional headers to send with this request.
		@type  headers: dict

		@return: The response to the request
		@rtype: U{HTTPResponse<http://docs.python.org/py3k/library/http.client.html#httpresponse-objects>}

		@raise Unauthorized: When the connection uses wrong credentials.
		@raise NotAcceptable: When the server cannot generate a response
			in the content type used by this connection (see also:
			L{set_content_handler}).
		@raise InternalServerError: When the server has some internal
			error.
		"""
		url = self._sanitize_url( url )
		return self.send( 'DELETE', url, headers=headers )
	
	def __eq__( self, other ):
		return self.host == other.host and self.port == other.port and \
			self.user == other.user and \
			self.passwd == other.passwd and \
			self.use_ssl == other.use_ssl

class RestAuthResource:
	"""
	Superclass for L{user<user.User>} and L{group<group.Group>} objects.
	The private methods of this class do nothing but prefix all request URLs
	with the prefix of that class (i.e. /users/).
	"""

	def _get( self, url, params={}, headers={} ):
		"""
		Internal method that prefixes a GET request with the resource
		name and passes the request to L{get}.
		"""
		url = '%s%s'%( self.__class__.prefix, url )
		return self.conn.get( url, params, headers )
	
	def _post( self, url, params={}, headers={} ):
		"""
		Internal method that prefixes a POST request with the resources
		name and passes the request to L{post}.
		
		"""
		url = '%s%s'%( self.__class__.prefix, url )
		return self.conn.post( url, params, headers )
	
	def _put( self, url, params={}, headers={} ):
		"""
		Internal method that prefixes a PUT request with the resources
		name and passes the request to L{put}.
		
		"""
		url = '%s%s'%( self.__class__.prefix, url )
		return self.conn.put( url, params, headers )
	
	def _delete( self, url, headers={} ):
		"""
		Internal method that prefixes a DELETE request with the
		resources name and passes the request to L{delete}.
		
		"""
		url = '%s%s'%( self.__class__.prefix, url )
		return self.conn.delete( url, headers )

