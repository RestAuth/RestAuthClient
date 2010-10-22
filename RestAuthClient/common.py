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

import os, json, base64
try:
	from RestAuthClient.errors import *
except ImportError:
	from errors import *

try:
	from urllib.parse import quote, urlencode
except ImportError:
	# this is for python 2.x and earlier
	from urllib import quote, urlencode

class RestAuthConnection:
	"""
	An instance of this class represents a connection to a RestAuth service.
	"""
	
	def __init__( self, host, port, user, passwd, use_ssl=True, cert='' ):
		"""
		Initialize a new connection to a RestAuth service. 
		
		Note that the constructor does not verify that the connection
		actually works. Since HTTP is stateless, there is no way of
		knowing if a connection working now will still work 0.2 seconds
		from now. 		

		@param host: The hostname of the RestAuth service
		@type  host: str
		@param port: The port the RestAuth service listens on
		@type  port: int
		@param user: The service name to use for authenticating with 
			RestAuth
		@type  user: str
		@param passwd: The password to use for authenticating with
			RestAuth.
		@type  passwd: str
		@param use_ssl: Wether or not to use SSL.
		@type  use_ssl: bool
		@param cert: The certificate to use when using SSL.
		@type  cert: str
		"""
		self.host = host
		self.port = port
		self.user = user
		self.passwd = passwd
		self.use_ssl = True
		self.cert = cert
	
		# pre-calculate the auth-header so we only have to do this once:
		self.set_credentials( user, passwd )

	def set_credentials( self, user, passwd ):
		"""
		Set the password for the given user. This method is
		automatically is also called by the constructor.

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

		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500

		@todo: catch 401/403 codes
		@todo: actually use SSL
		"""
		if self.auth_header:
			headers['Authorization'] = self.auth_header

		headers['Accept'] = 'application/json'
	
		# TODO: alternatively use an HTTPS connection
		conn = client.HTTPConnection( self.host, self.port )

		conn.request( method, url, body, headers )
		response = conn.getresponse()
		if response.status == 400:
			raise BadRequest( response )
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

		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
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
		@param params: The query parameters for this request. A
			dictionary of key/value pairs that is passed to
			U{quote<http://docs.python.org/py3k/library/urllib.parse.html#urllib.parse.quote>}.
		@type  params: dict
		@param headers: Additional headers to send with this request.
		@type  headers: dict

		@return: The response to the request
		@rtype: U{HTTPResponse<http://docs.python.org/py3k/library/http.client.html#httpresponse-objects>}

		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		"""
		headers['Content-Type'] = 'application/json'
		url = self._sanitize_url( url )
		body = json.dumps( params )
		return self.send( 'POST', url, body, headers )

	def put( self, url, params={}, headers={} ):
		"""
		Perform a PUT request on the connection. This method takes care
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

		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		"""
		headers['Content-Type'] = 'application/json'
		url = self._sanitize_url( url )
		body = json.dumps( params )
		return self.send( 'PUT', url, body, headers )

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

		@raise BadRequest: When the RestAuth service returns HTTP status code 400
		@raise InternalServerError: When the RestAuth service returns HTTP status code 500
		"""
		url = self._sanitize_url( url )
		return self.send( 'DELETE', url, headers=headers )
	
	def __eq__( self, other ):
		return self.host == other.host and self.port == other.port and \
			self.user == other.user and \
			self.passwd == other.passwd and \
			self.use_ssl == other.use_ssl and \
			self.cert == other.cert

class RestAuthResource:
	"""
	Superclass for L{user<user.User>} and L{group<group.Group>} objects.
	Exists to wrap http requests with the prefix of the given resource.
	"""

	def _get( self, url, params={}, headers={}, prefix=None ):
		"""
		Internal method that prefixes a GET request with the resources
		name.
		
		@raise BadRequest: When the RestAuth service returns HTTP status
			code 400
		@raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		"""
		if prefix:
			url = '%s%s'%( prefix, url )
		else:
			url = '%s%s'%( self.__class__.prefix, url )
		return self.conn.get( url, params, headers )
	
	def _post( self, url, params={}, headers={}, prefix=None ):
		"""
		Internal method that prefixes a POST request with the resources
		name.
		
		@raise BadRequest: When the RestAuth service returns HTTP status
			code 400
		@raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		"""
		if prefix:
			url = '%s%s'%( prefix, url )
		else:
			url = '%s%s'%( self.__class__.prefix, url )
		return self.conn.post( url, params, headers )
	
	def _put( self, url, params={}, headers={}, prefix=None ):
		"""
		Internal method that prefixes a PUT request with the resources
		name.
		
		@raise BadRequest: When the RestAuth service returns HTTP status
			code 400
		@raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		"""
		if prefix:
			url = '%s%s'%( prefix, url )
		else:
			url = '%s%s'%( self.__class__.prefix, url )
		return self.conn.put( url, params, headers )
	
	def _delete( self, url, headers={}, prefix=None ):
		"""
		Internal method that prefixes a DELETE request with the
		resources name.
		
		@raise BadRequest: When the RestAuth service returns HTTP status
			code 400
		@raise InternalServerError: When the RestAuth service returns
			HTTP status code 500
		"""
		if prefix:
			url = '%s%s'%( prefix, url )
		else:
			url = '%s%s'%( self.__class__.prefix, url )

		return self.conn.delete( url, headers )

