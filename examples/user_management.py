#!/usr/bin/env python3

# This demo script demos user management. It does not handle group management
# and managing membershipto users at all. If everything works, this script does
# not do any output.

import os, sys
sys.path.append( os.getcwd() ) # so we can import RestAuthClient

# common includes the connection handling code, restauth_user handles user-
# specific code:
from RestAuthClient import common, restauth_user

conn = common.RestAuthConnection( 'localhost', 8000, 'vowi', 'vowi', False )

# create a new user. the standard configuration does not allow spaces in the
# username, because this does not work on XMPP, email, ...
# The factory-methods for creating users guarantee that the user exist:
managed_user = restauth_user.User.create( conn, 'managed_user', 'password' )

# handle the password:
if managed_user.verify_password( 'password' ):
	pass
else:
	# password is not correct
	print( "Error: The password is not correct?" )

managed_user.set_password( 'new password' )

# Now we want to get a user from the service - this again guarantees that the
# user exists:
managed_user = restauth_user.User.get( conn, 'managed_user' )

# You can always just construct your own object, i.e. if you know that the user
# exists and do not want to hit the service. Here we create an instance of a
# user that does not in fact exist:
wrong_user = restauth_user.User( conn, 'wrong_user' )

# if performing any action on it, this will throw an error:
try:
	wrong_user.set_password( 'foobar' )
	print( "Error: wrong_user.set_password should throw an error!" )
except restauth_user.UserNotFound:
	pass

# of course, verify_password just returns false:
if wrong_user.verify_password( 'foobar' ):
	print( "Error: This should return false, the user doesn't exist!" )


# Next up, we manage some properties. Properties are just key/value pairs, the
# key is completely arbitrary. So it is possible for several services to use the
# same key to share settings for a specificic user.
props = managed_user.get_properties() # empty dictionary - not insteresting ;-)
managed_user.create_property( 'email', 'foo@bar.com' )

email = managed_user.get_property( 'email' )
if email != 'foo@bar.com':
	print( "Error: email should be foo@bar.com!" )

# Note that set_property overwrites an old value, while create_property throws
# an error if the given key already exists.
managed_user.set_property( 'email', 'new@bar.com' )
try:
	managed_user.create_property( 'email', 'old@bar.com' )
	print( "Error: create property should throw an error!" )
except restauth_user.PropertyExists:
	pass

# get all properties:
props = managed_user.get_properties() # this is { 'email': 'new@bar.com' }

# we can of course also delete the property:
managed_user.del_property( 'email' )

# finally, we delete all users we created:
managed_user.delete()
