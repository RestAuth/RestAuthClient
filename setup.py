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


import os, sys, shutil
from os.path import exists
from distutils.core import setup, Command
from subprocess import Popen, PIPE
from distutils.command.clean import clean as _clean

name = 'RestAuthClient'
url = 'https://fs.fsinf.at/wiki/RestAuth/Python'

class build_doc( Command ):
	description = "Build epydoc documentation."
	user_options = [('dest=', None, 'Output directory of documentation' )]

	def initialize_options( self ):
		self.dest = 'doc'

	def finalize_options( self ):
		command = self.get_command_name()
		options = self.distribution.command_options[ command ]

		if 'dest' in options:
			self.dest = options['dest'][1]

	def run( self ):
		try:
			# check for epydoc
			import epydoc
		except ImportError:
			print( "Error: epydoc is not installed." )
			sys.exit(1)

		html_dest = self.dest + '/html'
		if not os.path.exists( html_dest ):
			os.makedirs( html_dest )

		cmd = [ 'epydoc', '-v', '--html', '--name', name, '-o',
			html_dest, '--no-private', '-u', url, 
			'RestAuthClient' ]
		p = Popen( cmd )
		p.communicate()

class clean( _clean ):
	def run( self ):
		for directory in [ 'doc', 'build' ]:
			if os.path.exists( directory ):
				shutil.rmtree( directory )

		_clean.run( self )

def get_version():
	version = '0.1'
	if exists( '.version' ):
		print( 'get version from file...' )
		version = open( '.version' ).readlines()[0]
	elif exists( '.svn' ):
		cmd = [ 'svn', 'info' ]
		p = Popen( cmd, stdout=PIPE )
		stdin, stderr = p.communicate()
		lines = stdin.decode( "utf-8" ).split( "\n" )
		line = [ line for line in lines if line.startswith( 'Revision' ) ][0]
		version = '0.0-' + line.split( ': ' )[1].strip()
	return version

class version( Command ):
	description = "Print version and exit."
	user_options = []

	def initialize_options( self ): pass
	def finalize_options( self ): pass
	def run( self ):
		print( get_version() )

class test( Command ):
	description = "Run test suite."
	user_options = []

	def initialize_options( self ): pass
	def finalize_options( self ): pass
	def run( self ):
		import unittest
		from tests import users

		for mod in [ users ]:
			loader = unittest.TestLoader()
			suite = loader.loadTestsFromModule( mod )
			unittest.TextTestRunner(verbosity=1).run(suite)



setup(
	name=name,
	version=get_version(),
	description='RestAuth client library',
	author='Mathias Ertl',
	author_email='mati@fsinf.at',
	url = url,
	packages=['RestAuthClient'],
	cmdclass = { 'build_doc': build_doc, 'clean': clean, 'version': version,
		'test': test }
)
