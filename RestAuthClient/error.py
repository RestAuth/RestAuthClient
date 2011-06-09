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
This module collects various general exceptions that might be thrown on many 
different (or all) RestAuth methods.

.. moduleauthor:: Mathias Ertl <mati@fsinf.at>
"""

from RestAuthCommon.error import RestAuthImplementationException, RestAuthRuntimeException

class UnknownStatus( RestAuthImplementationException ):
	"""
	Thrown when a method returns an unexpected status.
	
	This exception can be thrown by every method that interacts with the
	RestAuth service.
	"""
	pass
	
class HttpException( RestAuthRuntimeException ):
	"""
	Thrown when the HTTP request throws an execption. This most likely means that the RestAuth
	server is unreachable.
	
	:param Exception cause: The exception causing this exception to be created.
	"""
	def __init__( self, cause ):
		self.cause = cause
		self.value = str(cause)
		
	def get_cause( self ):
		"""
		Get the exception that caused this exception.
		
		:return: The exception that caused this exception
		:rtype: Exception
		"""
		return self.cause
