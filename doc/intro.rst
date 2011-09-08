Guide
=====

The **RestAuthClient** library consists of four modules, each containing one important class:

* :py:mod:`~RestAuthClient.common` contains :py:class:`~.common.RestAuthConnection` which represents
  a connection to a RestAuth service.
* :py:mod:`~RestAuthClient.restauth_user` contains the :py:class:`~.restauth_user.User` class which
  represents a user in the RestAuth service.
* :py:mod:`~RestAuthClient.group` contains the :py:class:`~.group.Group` class which represents a
  group in the RestAuth service.
* :py:mod:`~RestAuthClient.error` is a collection of exceptions that may be thrown by the above
  modules and its member methods/classes.
  
To use RestAuth, you will always have to create a :py:class:`~.common.RestAuthConnection` first and
then use it to get users or groups.

The following example should give you a very good idea of how the library handles, error handling is
skipped for the sake of clarity. Please see the :ref:`guide_error-handling` section for the
exceptions used in this library.

.. code-block:: python

   from RestAuthClient import common, restauth_user, group
   
   # create a connection to the RestAuth service. The service must already be configured using the
   # restauth-service commandline script.
   conn = common.RestAuthConnection( 'https://auth.example.com', 'service', 'password' )
   
   # create a *new* user named 'foobar', and do some interesting things:
   user = restauth_user.create( conn, 'foobar', 'password' )
   if not user.verify_password( 'wrong password' ):
       print( 'ERROR: User has wrong password!' ) # never happens in this example, of course
       
   user.set_property( 'key', 'value' )
   props = user.get_properties() # returns {'key': 'value'}
   
   # If performance is critical, do not use the factory methods to get user objects, instead
   # reference them directly:
   user = restauth_user.User( conn, 'foobar' )
   user.verify_password( 'password' )
   
   # Groups work in much the same way as users:
   group = group.get( conn, 'groupname' ) # verifies that the group exists
   group.add_user( user ) # may also just be the username!
   group.get_members() # returns a list with the User element
   

.. _guide_error-handling:

Error handling
--------------

Like all RestAuth client libraries, the python client library features many custom exceptions with a
multi-leveled inheritance model. This allows you to handle problems with whatever granularity you
want.

Since the Python library is the reference implementation, many other libraries feature a similar or
even identical Exception class-hierarchy. Since both the `RestAuth server reference implementation
<https://server.restauth.net`_ and RestAuthClient use the same exceptions for error handling, most
exceptions are located in :py:mod:`RestAuthCommon.errors`.

RestAuthException
+++++++++++++++++

:py:class:`~.error.RestAuthException` is the base class for all exceptions related to RestAuth calls.
If you just want to be sure that any exception is handled, you should catch this exception:

.. code-block:: python

   from RestAuthClient.common import RestAuthConnection
   from RestAuthClient.restauth_user import user_get
   from RestAuthClient.errors import RestAuthException

   conn = new RestAuthConnection( "https://auth.example.com", "service", "password" )
   try:
       user = user_get( conn, "username" )
       # ...
   except RestAuthException:
       print( "Some error related to RestAuth" )

RestAuthImplementationException
+++++++++++++++++++++++++++++++                         

:py:class:`~.error.RestAuthImplementationException` is a superclass for all exceptions that should
never occur in a production environment and generally hint at a bug in either the server or the
client library. 

RestAuthSetupException
++++++++++++++++++++++

A subclass of :py:class:`~.error.RestAuthSetupException` indicates a problem with either the client
or server configuration and shouldn't happen if a working configuration hasn't changed. This usually
means that the person running the library can and should do something about the problem.

RestAuthError
+++++++++++++

A subclass of :py:class:`.error.RestAuthError` indicates a "normal" error that is bound to happen
sooner or later. This includes setting properties for users that don't exist, removing users that
don't exist and so on. Every client using this library should definetly handle this exception (or
its subclasses).

Summary
+++++++

The exception hierarchy basically means that you can catch exactly those exceptions that you want to
handle. Finally, here is a more complex example:

.. code-block:: python

   from RestAuthClient.common import RestAuthConnection
   from RestAuthClient.restauth_user import user_get
   from RestAuthClient.errors import RestAuthException

   conn = new RestAuthConnection( "https://auth.example.com", "user", "password" )
   try:
       user = user_get( conn, "username" )
       # ...
   except RestAuthImplementationException:
       print( "You must be debugging a new server application?" )
   except RestAuthRuntimeException:
       print( "Some runtime error occured that the client can't do anything about." )
   except Unauthorized: #actually a subclass of RestAuthSetupException below
       print( "Failed to authenticate with the RestAuth server" )
   except RestAuthSetupException:
       print( "Have you setup your server correctly?" )
   except RestAuthError:
       print( "User with name username doesn't exist" )
   except RestAuthException:
       print( "This should never happen, everything is caught above" )
