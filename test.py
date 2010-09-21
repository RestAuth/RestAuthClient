#!/usr/bin/python3

import group, restauth_user, common

conn = common.RestAuthConnection( 'localhost', 8000, 'vowi', 'vowi', False )
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
