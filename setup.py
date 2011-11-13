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

import os, re, sys, shutil, time
from distutils.core import setup, Command
from subprocess import Popen, PIPE
from distutils.command.clean import clean as _clean
from distutils.command.build import build as _build

name = 'RestAuthClient'
url = 'https://python.restauth.net'

LATEST_RELEASE = '0.5.0'

class build_doc( Command ):
	description = "Build documentation."
	user_options = []

	def initialize_options( self ):
		pass

	def finalize_options( self ):
		command = self.get_command_name()

	def run( self ):
		version = get_version()
		os.environ['SPHINXOPTS'] = '-D release=%s -D version=%s'%(version, version)
		os.environ['LATEST_RELEASE'] = LATEST_RELEASE
		
		cmd = [ 'make', '-C', 'doc', 'html' ]
		p = Popen( cmd )
		p.communicate()

class clean( _clean ):
	def run( self ):
		if os.path.exists( 'build' ):
			shutil.rmtree( 'build' )
		if os.path.exists( 'dist' ):
			shutil.rmtree( 'dist' )
		coverage_path = os.path.join( 'doc', 'coverage' )
		if os.path.exists( coverage_path ):
			shutil.rmtree( coverage_path )
		if os.path.exists( 'MANIFEST' ):
			os.remove( 'MANIFEST' )

		cmd = [ 'make', '-C', 'doc', 'clean' ]
		p = Popen( cmd )
		p.communicate()

		_clean.run( self )

def get_version():
	version = LATEST_RELEASE
	if os.path.exists( '.version' ):
		version = open( '.version' ).readlines()[0]
	elif os.path.exists( '.git' ): # get from git
		date = time.strftime( '%Y.%m.%d' )
		cmd = [ 'git', 'describe' ]
		p = Popen( cmd, stdout=PIPE )
		version = p.communicate()[0].decode( 'utf-8' )
	elif os.path.exists( 'debian/changelog' ): # building .deb
		f = open( 'debian/changelog' )
		version = re.search( '\((.*)\)', f.readline() ).group(1)
		f.close()
		
		if ':' in version: # strip epoch:
			version = version.split( ':', 1 )[1]
		version = version.rsplit( '-', 1 )[0] # strip debian revision
	return version.strip()

class version( Command ):
	description = "Print version and exit."
	user_options = []

	def initialize_options( self ): pass
	def finalize_options( self ): pass
	def run( self ):
		print( get_version() )

def run_test_suite( host, user, passwd ):
	import unittest
	from tests import connection, users, groups

	for mod in [ connection, users, groups ]:
		mod.rest_host = host
		mod.rest_user = user
		mod.rest_passwd = passwd

		loader = unittest.TestLoader()
		suite = loader.loadTestsFromModule( mod )
		unittest.TextTestRunner(verbosity=1).run(suite)


class test( Command ):
	description = "Run test suite."
	user_options = [
		( 'user=', 'u', 'Username to use vor RestAuth server' ),
		( 'password=', 'p', 'Password to use vor RestAuth server' ),
		( 'host=', 'h', 'URL of the RestAuth server (ex: http://auth.example.com)')]

	def initialize_options( self ): 
		self.user = 'vowi'
		self.passwd = 'vowi'
		self.host = 'http://[::1]:8000'

	def finalize_options( self ): pass

	def run( self ):
		common_path = os.path.join( '..', 'restauth-common', 'python' )
		if os.path.exists( common_path ):
			sys.path.insert( 0, common_path )
			
		run_test_suite( self.host, self.user, self.passwd )

class coverage( Command ):
	description = "Run test suite and generate code coverage analysis."
	user_options = [
		( 'output-dir=', 'o', 'Output directory for coverage analysis' ),
		( 'user=', 'u', 'Username to use vor RestAuth server' ),
		( 'password=', 'p', 'Password to use vor RestAuth server' ),
		( 'host=', 'h', 'URL of the RestAuth server (ex: http://auth.example.com)') ]
	

	def initialize_options( self ): 
		self.user = 'vowi'
		self.passwd = 'vowi'
		self.host = 'http://[::1]:8000'
		self.dir = 'doc/coverage'

	def finalize_options( self ): pass


	def run( self ):
		try:
			import coverage
		except ImportError:
			print( "You need coverage.py installed." )
			return
		common_path = os.path.join( '..', 'restauth-common', 'python' )
		if os.path.exists( common_path ):
			sys.path.insert( 0, common_path )

		if not os.path.exists( self.dir ):
			os.makedirs( self.dir )

		exclude_list = [ 'raise UnknownStatus.*' ]

		cov = coverage.coverage( include='RestAuthClient/*' )
		cov.start()
		run_test_suite( self.host, self.user, self.passwd )
		cov.stop()
		cov.html_report( directory=self.dir )
		cov.report()

setup(
	name=name,
	version=str(get_version()),
	description='RestAuth client library',
	long_description = """RestAuthClient is the client reference implementation of the
`RestAuth protocol <https://restauth.net/Specification>`_. RestAuth is a system providing shared
authentication, authorization and preferences. The full documentation of this library is available
at `python.restauth.net <https://python.restauth.net>`_.

This library requires `RestAuthCommon <https://common.restauth.net>`_
(`PyPI <http://pypi.python.org/pypi/RestAuthCommon/>`_).
""",
	author='Mathias Ertl',
	author_email='mati@restauth.net',
	url = url,
	download_url = 'https://python.restauth.net/download/',
	packages=['RestAuthClient'],
	cmdclass = { 'build_doc': build_doc, 'clean': clean, 'version': version,
		'test': test, 'coverage': coverage },
	license = "GNU General Public License (GPL) v3",
	requires = ['RestAuthCommon', ],
	classifiers = [
		"Programming Language :: Python",
		"Programming Language :: Python :: 3",
		"Operating System :: OS Independent",
		"Environment :: Other Environment",
		"Development Status :: 4 - Beta",
		"License :: OSI Approved :: GNU General Public License (GPL)",
		"Intended Audience :: Developers",
		"Intended Audience :: System Administrators",
		"Topic :: System :: Systems Administration :: Authentication/Directory",
		"Topic :: Internet :: WWW/HTTP",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Environment :: Web Environment",
	]
)
