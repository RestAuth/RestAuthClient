#!/usr/bin/python3

import Group, User, RestAuthCommon

conn = RestAuthCommon.RestAuthConnection( 'localhost', 8000, 'vowi', 'vowi', False )
u = User.User.get( conn, 'user1' )


print( User.User.get_all( conn ) )
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
g = Group.Group( conn, 'vowi1' )
print( g.get_members() )
g.add_user( User.User( conn, 'user5') )
print( g.get_members() )
print( Group.Group.get_all( conn ) )

try:
	print( "Get non-existing user... ", end="" )
	u_ne = User.User.get( conn, 'user_foobar' )
	print( "FOUND!?" )
except User.UserNotFound:
	print( "ok (not found)." )
