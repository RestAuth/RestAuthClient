try:
	from http import client
except ImportError:
	# this is for python 2.x and earlier
	import httplib as client

import os, base64

try:
	from urllib.parse import quote_plus, urlencode
except ImportError:
	# this is for python 2.x and earlier
	from urllib import quote_plus, urlencode

class RestAuthConnection:
	"""
	A connection to a RestAuth service.
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
		@param user: The service name to use for authenticating with RestAuth
		@type  user: str
		@param passwd: The password to use for authenticating with
			RestAuth.
		@type  passwd: str
		@param use_ssl: Wether or not to use SSL.
		@type  use_ssl: bool
		@param cert: The certificate to use when using SSL.
		@type  cert: str
		@todo: actually use SSL
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

	def send( self, method, url, body=None, headers={}):
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
		"""
		if self.auth_header:
			headers['Authorization'] = self.auth_header

		headers['Content-Type'] = 'application/json'
		headers['Accept'] = 'application/json'
	
		# TODO: alternatively use an HTTPS connection
		conn = client.HTTPConnection( self.host, self.port )
		print( '%s: %s'%(method, url ) )
		if body:
			print( 'body: %s'%(body) )

		conn.request( method, url, body, headers )
		return conn.getresponse()

	def _sanitize( self, url, params ):
		params = urlencode( params )

		# make sure that it starts and ends with /, cut double-slashes:
		url = '%s/'%( os.path.normpath( url ) )
		if not url.startswith( '/' ):
			url = '/%s'%(url)
		url = quote_plus( url, '/' )
		return url, params

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
			U{quote_plus<http://docs.python.org/py3k/library/urllib.parse.html#urllib.parse.quote_plus>}.
		@type  params: dict
		@param headers: Additional headers to send with this request.
		@type  headers: dict

		"""
		url, qs = self._sanitize( url, params )
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
			U{quote_plus<http://docs.python.org/py3k/library/urllib.parse.html#urllib.parse.quote_plus>}.
		@type  params: dict
		@param headers: Additional headers to send with this request.
		@type  headers: dict

		"""
		url, body = self._sanitize( url, params )
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
			U{quote_plus<http://docs.python.org/py3k/library/urllib.parse.html#urllib.parse.quote_plus>}.
		@type  params: dict
		@param headers: Additional headers to send with this request.
		@type  headers: dict

		"""
		url, body = self._sanitize( url, params )
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

		"""
		url, body = self._sanitize( url, {} )
		return self.send( 'DELETE', url, headers=headers )

class RestAuthResource:
	"""
	Superclass for L{User} and L{Group} objects. Exists to wrap http
	requests with the prefix of the given resource.
	"""

	def _get( self, url, params={}, headers={}, prefix=None ):
		"""
		Internal method that prefixes a GET request with the resources
		name.
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
		"""
		if prefix:
			url = '%s%s'%( prefix, url )
		else:
			url = '%s%s'%( self.__class__.prefix, url )

		return self.conn.delete( url, headers )
	
	def handle_status_codes( self, body, response ):
		"""
		@todo: relocate this to some place more sensible.
		@todo: catch 401/403 codes
		"""
		if response.status == 400:
			raise BadRequest( body, resp.read() )
		elif response.status == 500:
			raise InternalServerError( resp.read() )
		else:   
			raise UnknownStatus( resp.status, resp.read() )


