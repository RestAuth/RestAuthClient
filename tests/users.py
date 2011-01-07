# -*- coding: utf-8 -*-

import unittest
from RestAuthClient.errors import *
from RestAuthClient.common import RestAuthConnection
from RestAuthClient import restauth_user

host = 'http://localhost:8000'
user = 'vowi'
passwd = 'vowi'

simple = u'mati'
space = u'mati space'
uniname = u"mati \u6110"
unipass = u"mati \u6111"

class BasicTests(unittest.TestCase):
	def setUp( self ):
		self.conn = RestAuthConnection( host, user, passwd )

		if restauth_user.get_all( self.conn ):
			raise RuntimeError( "Found leftover users." )

	def tearDown( self ):
		for user in restauth_user.get_all( self.conn ):
			user.delete()

	def test_createUser( self ):
		user = restauth_user.create( self.conn, simple, "password" )

		users = restauth_user.get_all( self.conn )
		self.assertEqual( 1, len( users ) )
		self.assertEqual( user, users[0] )
		self.assertEqual( user, restauth_user.get( self.conn, simple ) )
	
	def test_createUserWithSpace( self ):
		user = restauth_user.create( self.conn, space, "password" )

		users = restauth_user.get_all( self.conn )
		self.assertEqual( 1, len( users ) )
		self.assertEqual( user, users[0] )
		self.assertEqual( user, restauth_user.get( self.conn, space ) )
	
	def test_createUserUnicode( self ):
		user = restauth_user.create( self.conn, uniname, "password" )

		users = restauth_user.get_all( self.conn )
		self.assertEqual( 1, len( users ) )
		self.assertEqual( user, users[0] )
		self.assertEqual( user, restauth_user.get( self.conn, uniname ) )
	
	def test_createInvalidUser( self ):
		args = [self.conn, "foo/bar", "password"]
		self.assertRaises( PreconditionFailed, restauth_user.create, *args )

		self.assertEqual( [], restauth_user.get_all( self.conn ) )

	def test_verifyPassword( self ):
		user = restauth_user.create( self.conn, uniname, unipass )
		self.assertTrue( user.verify_password( unipass ) )
		self.assertFalse( user.verify_password( "whatever" ) )

	def test_verifyPasswordInvalidUser( self ):
		user = restauth_user.User( self.conn, uniname )
		self.assertFalse( user.verify_password( unipass ) )

	def test_setPassword( self ):
		newpass = "new " + unipass

		user = restauth_user.create( self.conn, uniname, unipass )
		self.assertTrue( user.verify_password( unipass ) )
		self.assertFalse( user.verify_password( newpass ) )

		user.set_password( "new " + unipass )
		self.assertFalse( user.verify_password( unipass ) )
		self.assertTrue( user.verify_password( newpass ) )

	def test_setPasswordInvalidUser( self ):
		user = restauth_user.User( self.conn, uniname )
		try:
			user.set_password( unipass )
			self.fail()
		except ResourceNotFound as e:
			self.assertEqual( e.get_type(), "user" )


