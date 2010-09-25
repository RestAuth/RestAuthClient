#!/usr/bin/python3

import unittest
import group, restauth_user, common

class RestAuthTestCase( unittest.TestCase ):
	def setUp( self ):
		self.conn = common.RestAuthConnection( 'localhost', 8000, 'vowi', 'vowi', False )

		if restauth_user.User.get_all( self.conn ):
			raise RuntimeError( "Left over users!" )

		if group.Group.get_all( self.conn ):
			raise RuntimeError( "Left over groups!" )

class TestAddUser( RestAuthTestCase ):
	def test_add_user_one( self ):
		print( "AddUser: 1" )

	def test_add_user_two( self ):
		print( "AddUser: 2" )
	
	def test_add_user_three( self ):
		print( "AddUser: 3" )

class TestDelUser( RestAuthTestCase ):
	def test_del_user_one( self ):
		print( 'DelUser: 1' )
	
	def test_del_user_two( self ):
		print( 'DelUser: 2' )
	
	def test_del_user_three( self ):
		print( 'DelUser: 3' )

unittest.main()

import sys
sys.exit()

u = restauth_user.User.get( conn, 'user1' )


print( restauth_user.User.get_all( conn ) )
u.set_password( 'foo bar' )
if u.verify_password( 'foo bar' ):
	print( 'verified' )
u.verify_password( 'wrongpass' )
u.set_password( 'wrongpass' )
u.verify_password( 'wrongpass' )

u.get_properties()
u.create_property( 'foo', 'foo value' )
try:
	u.create_property( 'foo', 'foo value new' )
	print( "ERROR: create_property didn't fail the second time" )
except:
	pass

print( '\n\n\nTest user properties' )
print( u.get_properties() )
print( u.get_property( 'foo' ) )

u.set_property( 'bar', 'bar value' )
print( u.get_properties() )
print( u.get_property( 'bar' ) )
u.set_property( 'bar', 'bar value new' )
print( u.get_properties() )
print( u.get_property( 'bar' ) )

u.del_property( 'foo' )
u.del_property( 'bar' )
print( u.get_properties() )

print( "\n\n\nTest groups" )
g = group.Group( conn, 'vowi1' )
print( g.get_members() )
g.add_user( restauth_user.User( conn, 'user5') )
print( g.get_members() )
print( group.Group.get_all( conn ) )

try:
	print( "Get non-existing user... ", end="" )
	u_ne = restauth_user.User.get( conn, 'user_foobar' )
	print( "FOUND!?" )
except restauth_user.UserNotFound:
	print( "ok (not found)." )
