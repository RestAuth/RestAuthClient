#!/usr/bin/python3

"""
This is a test script using (hopefully) all the features of RestAuthClient.py.
It accepts no parameters, just execute it to see if everything still works.

This is not designed to be very sophisticated, it creates users and groups and
deletes them afterwards. If an error occurs, the script exits right away and
leaves everything as it is at that moment.

You might want to change the username and password at the start. The info here
corresponds to what is added when the server is started with the test.sh script
shipping with RestAuth.
"""

import sys
from RestAuthClient import common, group, restauth_user
from RestAuthClient.errors import *

conn = common.RestAuthConnection( 'http://[::1]:8000', 'vowi', 'vowi', True )

# verify initial state:
users = restauth_user.get_all( conn )
if users:
	print( users )
	raise RuntimeError( "Left over users:" )

groups = group.get_all( conn )
if groups:
	print( groups )
	raise RuntimeError( "Left over groups!" )

##########################
### BASIC USER TESTING ###
##########################

print( 'Creating test users... ', end='' )
user0 = restauth_user.create( conn, 'user0', 'password0' )
user1 = restauth_user.create( conn, 'user1', 'password1' )
user2 = restauth_user.create( conn, 'user2', 'password2' )
user3 = restauth_user.create( conn, 'user3', 'password3' )
user4 = restauth_user.create( conn, 'user4', 'password4' )
user5 = restauth_user.create( conn, 'user5', 'password5' )
user6 = restauth_user.create( conn, 'user6', 'password6' )
user7 = restauth_user.create( conn, 'user7', 'password7' )
user8 = restauth_user.create( conn, 'user8', 'password8' )
user9 = restauth_user.create( conn, 'user9', 'password9' )
print( 'Ok.' )

print( 'Verifing added users... ', end='' )
user_list = restauth_user.get_all( conn )
if len( user_list ) == 10:
	print( 'Ok.' )
else:
	print( 'FAILED - counted %s users in RestAuth, but added 10'%(len(user_list)) )
	sys.exit(1)

print( 'Verifying some passwords...', end='' )
if not user0.verify_password( 'password0' ):
	print( 'FAILED - correct password could not be verifyied.' )
	sys.exit(1)
if not user9.verify_password( 'password9' ):
	print( 'FAILED - correct password could not be verifyied.' )
	sys.exit(1)
if user3.verify_password( 'wrong password' ):
	print( 'FAILED - wrong password was correct?' )
	sys.exit(1)
if user5.verify_password( 'wrong password' ):
	print( 'FAILED - wrong password was correct?' )
	sys.exit(1)
print( 'Ok.' )

print( 'Trying to create already existing user... ', end='' )
try:
	userx = restauth_user.create( conn, 'user0', 'password-foobar' )
	print( 'FAILED - successfully created user?' )
	sys.exit(1)
except restauth_user.UserExists:
	pass

# verify that we still have 10 users?
user_list = restauth_user.get_all( conn ) 
if not len( user_list ) == 10:
	print( 'FAILED - We no longer have 10 users in RestAuth!' )
	sys.exit(1)
# verify that the old password still checks out?
if not user0.verify_password( 'password0' ):
	print( 'FAILED - It seems like the password was changed?' )
	sys.exit(1)
print( 'Ok.' )

print( 'Trying to get some users... ', end='' )
user0 = restauth_user.get( conn, 'user0' )
user1 = restauth_user.get( conn, 'user1' )
print( 'Ok.' )
try:
	print( 'Trying to get nonexistent user... ', end='' )
	user99 = restauth_user.get( conn, 'user99' )
	print( 'FAILED - GOT A USER???' )
	sys.exit(1)
except ResourceNotFound:
	print( 'Ok.' )
	
print( 'Updating some passwords... ', end='' )
user1.set_password( 'new password' )
if not user1.verify_password( 'new password' ):
	print( 'FAILED - new password does not verify...' )
	sys.exit(1)
if user1.verify_password( 'password1' ):
	print( 'FAILED - old password still verifies...' )
	sys.exit(1)
# from some user that doesn't exist:
try:
	user99 = restauth_user.User( conn, 'user99' )
	user99.set_password( 'new password' )
	print( 'FAILED - set password for non-existing user' )
	sys.exit(1)
except ResourceNotFound:
	pass

user1.set_password( 'password1' )
print( 'Ok.' )

#######################
### USER PROPERTIES ###
#######################

print( "Creating some test properties... ", end='' )
user1.create_property( 'email', 'user1@example.com' )
user2.create_property( 'email', 'user2@example.com' )
user3.create_property( 'email', 'user3@example.com' )
user4.create_property( 'email', 'user4@example.com' )
user5.create_property( 'email', 'user5@example.com' )
user6.create_property( 'email', 'user6@example.com' )
user7.create_property( 'email', 'user7@example.com' )
user8.create_property( 'email', 'user8@example.com' )
user9.create_property( 'email', 'user9@example.com' )
print( "Ok." )

print( "Getting some properties... ", end="" )
mail = user1.get_property( 'email' )
if mail != "user1@example.com":
	print( "FAILED - got wrong mail address: %s"%mail )
	sys.exit(1)
try:
	user1.get_property( 'wrong property' )
	print( 'FAILED - got wrong property' )
	sys.exit(1)
except ResourceNotFound:
	pass

try: 
	user99 = restauth_user.User( conn, 'user99' )
	user99.get_property( 'email' )
	print( 'FAILED - got property of non-existing user...' )
	sys.exit(1)
except ResourceNotFound:
	pass
print( "Ok." )

print( 'Trying to create already existing property... ', end='' )
try:
	user1.create_property( 'email', 'new@example.com' )
	print( 'FAILED - could create a property that already exists.' )
	sys.exit(1)
except restauth_user.PropertyExists:
	mail = user1.get_property( 'email' )
	if mail != "user1@example.com":
		print( "FAILED - got wrong mail address..." )
		sys.exit(1)
print( 'Ok.' )

print( 'Set/overwrite some properties... ', end='' )
# set new:
user1.set_property( 'skin', 'bazinga' )
skin = user1.get_property( 'skin' )
if skin != "bazinga":
	print( "FAILED - got wrong skin..." )
	sys.exit(1)

# overwrite:
user1.set_property( 'email', 'new@example.com' )
mail = user1.get_property( 'email' )
if mail != "new@example.com":
	print( "FAILED - got wrong mail address..." )
	sys.exit(1)
print( 'Ok.' )

print( 'Get all properties... ', end='' )
# at this point, we should have email and skin:
props = user1.get_properties()
if not len( props.keys() ) == 2:
	print( 'Wrong number of properties' )
	sys.exit(1)
if not props['email'] == 'new@example.com':
	print( 'Wrong email address' )
	sys.exit(1)
if not props['skin'] == 'bazinga':
	print( 'Wrong skin' )
	sys.exit(1)
print( 'Ok.' )

print( 'Delete some properties... ', end='' )
user1.remove_property( 'skin' )
try:
	skin = user1.get_property( 'skin' )
	print( 'get_property returned deleted property' )
	sys.exit(1)
except ResourceNotFound:
	pass

props = user1.get_properties()
if 'skin' in props:
	print( 'get_properties returned deleted property' )
	sys.exit(1)
print( 'Ok.' )

#####################
### GROUP TESTING ###
#####################
print( 'Creating test groups... ', end='' )
group0 = group.create( conn, 'group0' )
group1 = group.create( conn, 'group1' )
group2 = group.create( conn, 'group2' )
group3 = group.create( conn, 'group3' )
group4 = group.create( conn, 'group4' )
group5 = group.create( conn, 'group5' )
group6 = group.create( conn, 'group6' )
group7 = group.create( conn, 'group7' )
group8 = group.create( conn, 'group8' )
group9 = group.create( conn, 'group9' )
print( 'Ok.' )

print( 'Try to create already existing group... ', end='' )
try:
	group0 = group.create( conn, 'group0' )
	print( 'Error: Successfully created existing group' )
except group.GroupExists:
	pass
print( 'Ok.' )

print( 'Get all groups... ', end='' )
groups = group.get_all( conn )
if len( groups ) != 10:
	print( 'Error: Got %s groups, but created 10!'%(len(groups)) )
	sys.exit(1)
print( 'Ok.' )

print( 'Adding users to groups... ', end='' )
group0.add_user( user0 )
group1.add_user( user1 )

new_group = group.Group( conn, 'new group' ) # this doesn't exist!

try:
	# verify that new_group is gone
	group.get( conn, 'new group' )
	print( "Error: deleted group is still there!" )
	sys.exit( 1 )
except ResourceNotFound:
	pass

wrong_user = restauth_user.User( conn, 'user99' )

wrong_group = group.Group( conn, 'wrong_group' ) # this doesn't exist!
try:
	wrong_group.add_user( user0 )
	print( 'Error: added user to non-existing group!' )
	sys.exit(1)
except ResourceNotFound:
	pass

try:
	new_group.add_user( wrong_user )
	print( 'Error: Successfully added non-existing user to non-existing group!' )
	sys.exit(1)
except ResourceNotFound:
	pass

group2.add_user( user2 )
group3.add_user( user3 )
group4.add_user( user4 )
group5.add_user( user5 )
group6.add_user( user6 )
group7.add_user( user7 )
group8.add_user( user8 )
group9.add_user( user9 )

# test membership for each user in each group
for i in range(0,10):
	u = restauth_user.User( conn, 'user%s'%(i) )
	g = group.Group( conn, 'group%s'%(i) )
	g.is_member( u )

	members = g.get_members()
	if len( members ) != 1:
		print( "Wrong length of users!" )
		sys.exit(1)
	if members[0].name != u.name:
		print( "User has wrong username!" )
print( 'Ok.' )

print( 'Test recursive group memberships... ', end='' )
group0.add_group( group1 )
g0_members = group0.get_members()
g1_members = group1.get_members()
if g0_members != [ user0 ]:
	print( "Error: group0 has wrong members: %s"%(g0_members) )
	sys.exit(1)
if g1_members != [ user0, user1 ]:
	print( "Error: group1 has wrong members: %s"%(g1_members) )
	sys.exit(1)

group1.add_group( group2 )
g1_members = group1.get_members()
g2_members = group2.get_members()
if g1_members != [ user0, user1 ]:
	print( "Error: group1 has wrong members: %s"%(g1_members) )
	sys.exit(1)
if g2_members != [ user0, user1, user2 ]:
	print( "Error: group2 has wrong members: %s"%(g2_members) )
	sys.exit(1)
print( 'Ok.' )

###############
### CLEANUP ###
###############
print( 'Clean up test users... ', end='' )
user0.remove()
user1.remove()
user2.remove()
user3.remove()
user4.remove()
user5.remove()
user6.remove()
user7.remove()
user8.remove()
user9.remove()

group0.remove()
group1.remove()
group2.remove()
group3.remove()
group4.remove()
group5.remove()
group6.remove()
group7.remove()
group8.remove()
group9.remove()

# verify initial state:
users = restauth_user.get_all( conn )
if users:
	print( users )
	raise RuntimeError( "Left over users:" )

groups = group.get_all( conn )
if groups:
	print( groups )
	raise RuntimeError( "Left over groups!" )

print( 'Ok.' )
sys.exit(0)


u = restauth_user.get( conn, 'user1' )


print( restauth_user.get_all( conn ) )
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

u.remove_property( 'foo' )
u.remove_property( 'bar' )
print( u.get_properties() )

print( "\n\n\nTest groups" )
g = group.Group( conn, 'vowi1' )
print( g.get_members() )
g.add_user( restauth_user.User( conn, 'user5') )
print( g.get_members() )
print( group.get_all( conn ) )

try:
	print( "Get non-existing user... ", end="" )
	u_ne = restauth_user.get( conn, 'user_foobar' )
	print( "FOUND!?" )
except ResourceNotFound:
	print( "ok (not found)." )
