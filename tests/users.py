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
unikey = u"mati \u6112"
unival = u"mati \u6113"

class BasicTests( unittest.TestCase ):
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
	
	def test_getInvalidUser( self ):
		try:
			restauth_user.get( self.conn, "invalid" )
		except ResourceNotFound as e:
			self.assertEqual( "user", e.get_type() )

	def test_removeUser( self ):
		user = restauth_user.create( self.conn, uniname, unipass )
		user.delete()

		self.assertEqual( [], restauth_user.get_all( self.conn ) )
		try:
			restauth_user.get( self.conn, uniname )
			self.fail()
		except ResourceNotFound as e:
			self.assertEqual( "user", e.get_type() )

	def test_removeInvalidUser( self ):
		user = restauth_user.User( self.conn, "invalid" )
		try:
			user.delete()
		except ResourceNotFound as e:
			self.assertEqual( "user", e.get_type() )


class PropertyTests( unittest.TestCase ):
	def setUp( self ):
		self.conn = RestAuthConnection( host, user, passwd )
		if restauth_user.get_all( self.conn ):
			raise RuntimeError( "Found leftover users." )

		self.user = restauth_user.create( self.conn, uniname, unipass )

	def tearDown( self ):
		for user in restauth_user.get_all( self.conn ):
			user.delete()

	def test_createProperty( self ):
		self.user.create_property( unikey, unival )
		self.assertEqual( {unikey:unival}, self.user.get_properties() )
		self.assertEqual( unival, self.user.get_property( unikey ) )

	def test_createPropertyTwice( self ):
		self.user.create_property( unikey, unival )
		self.assertEqual( {unikey:unival}, self.user.get_properties() )
		self.assertEqual( unival, self.user.get_property( unikey ) )

		try:
			self.user.create_property( unikey, unival + "foo" )
			self.fail()
		except restauth_user.PropertyExists as e:
			# verify that the prop hasn't changed:
			self.assertEqual( {unikey:unival}, self.user.get_properties() )
			self.assertEqual( unival, self.user.get_property( unikey ) )

	def test_createPropertyWithInvalidUser( self ):
		user = restauth_user.User( self.conn, uniname + " foo" )
		try:
			user.create_property( unikey, unival )
			self.fail()
		except ResourceNotFound as e:
			self.assertEqual( "user", e.get_type() )

			# verify that no user was created:
			self.assertNotEqual( user, self.user )
			self.assertEqual( [ self.user ], restauth_user.get_all(self.conn) )

	def test_setProperty( self ):
		self.assertEqual( None, self.user.set_property( unikey, unival ) )
		self.assertEqual( {unikey:unival}, self.user.get_properties() )
		self.assertEqual( unival, self.user.get_property( unikey ) )

	def test_setPropertyTwice( self ):
		newunival = unival + " new"

		self.assertEqual( None, self.user.set_property( unikey, unival ) )
		self.assertEqual( {unikey:unival}, self.user.get_properties() )
		self.assertEqual( unival, self.user.get_property( unikey ) )
		
		self.assertEqual( unival, self.user.set_property( unikey, newunival ) )
		self.assertEqual( {unikey:newunival}, self.user.get_properties() )
		self.assertEqual( newunival, self.user.get_property( unikey ) )

	def test_setPropertyWithInvalidUser( self ):
		user = restauth_user.User( self.conn, uniname + " foo" )
		try:
			user.create_property( unikey, unival )
			self.fail()
		except ResourceNotFound as e:
			self.assertEqual( "user", e.get_type() )

			# verify that no user was created:
			self.assertNotEqual( user, self.user )
			self.assertEqual( [ self.user ], restauth_user.get_all(self.conn) )

	def test_removeProperty( self ):
		self.assertEqual( None, self.user.create_property( unikey, unival ) )
		
		self.user.del_property( unikey )
		self.assertEqual( {}, self.user.get_properties() )
		try:
			self.user.get_property( unikey )
			self.fail()
		except ResourceNotFound as e:
			self.assertEqual( "property", e.get_type() )
	
	def test_removeInvalidProperty( self ):
		self.user.create_property( unikey, unival )

		try:
			self.user.del_property( unikey + " foo" )
			self.fail()
		except ResourceNotFound as e:
			self.assertEqual( "property", e.get_type() )
			self.assertEqual( [ self.user ], restauth_user.get_all( self.conn ) )
			self.assertEqual( {unikey:unival}, self.user.get_properties() )
			self.assertEqual( unival, self.user.get_property( unikey ) )

	def test_removePropertyWithInvalidUser( self ):
		user = restauth_user.User( self.conn, "new user" )

		try:
			user.del_property( "foobar" )
		except ResourceNotFound as e:
			self.assertEqual( "user", e.get_type() )

	def test_removePropertyFromWrongUser( self ):
		"""
		Purpose of this test is to add a property to one user, and
		verify that deleting it from the *other* user does not delete it
		for the original user.
		"""

		user_2 = restauth_user.create( self.conn, "new user", "password" )
		self.user.create_property( unikey, unival )

		try:
			user_2.del_property( unikey )
		except ResourceNotFound as e:
			self.assertEqual( "property", e.get_type() )

		self.assertEqual( {}, user_2.get_properties() )

		self.assertEqual( {unikey:unival}, self.user.get_properties() )
		self.assertEqual( unival, self.user.get_property( unikey ) )

	def test_getInvalidProperty( self ):
		try:
			self.user.get_property( "foobar" )
		except ResourceNotFound as e:
			self.assertEqual( "property", e.get_type() )

	def test_getPropertiesInvalidUser( self ):
		user = restauth_user.User( self.conn, "foobar" )

		try:
			user.get_properties()
			self.fail()
		except ResourceNotFound as e:
			self.assertEqual( "user", e.get_type() )
