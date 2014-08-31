Guide
=====

The **RestAuthClient** library consists of four modules, each containing one important class:

* :py:mod:`~RestAuthClient.common` contains :py:class:`~.common.RestAuthConnection` which represents
  a connection to a RestAuth service.
* :py:mod:`~RestAuthClient.user` contains the :py:class:`~.user.RestAuthUser` class which
  represents a user in the RestAuth service.
* :py:mod:`~RestAuthClient.group` contains the :py:class:`~.group.RestAuthGroup` class which represents a
  group in the RestAuth service.
* :py:mod:`~RestAuthClient.error` is a collection of exceptions that may be thrown by the above
  modules and its member methods/classes.

To use RestAuth, you will always have to create a :py:class:`~.common.RestAuthConnection` first and
then use it to get users or groups.

The following example should give you a very good idea of how the library handles, error handling is
skipped for the sake of clarity. Please see the :ref:`guide_error-handling` section for the
exceptions used in this library.

.. code-block:: python

   from RestAuthClient.common import Connection
   from RestAuthClient.user import RestAuthUser
   from RestAuthClient.group import RestAuthGroup

   # create a connection to the RestAuth service. The service must already be configured using the
   # restauth-service commandline script.
   conn = RestAuthConnection('https://auth.example.com', 'service', 'password')

   # create a *new* user named 'foobar', and do some interesting things:
   user = RestAuthUser.create(conn, 'foobar', 'password')
   if not user.verify_password('wrong password'):
       print('ERROR: User has wrong password!')  # never happens in this example, of course

   user.set_property('key', 'value')
   props = user.get_properties()  # returns {'key': 'value'}

   # If performance is critical, do not use the factory methods to get user objects, instead
   # reference them directly:
   user = RestAuthUser(conn, 'foobar')
   user.verify_password('password')

   # Groups work in much the same way as users:
   group = RestAuthGroup.get(conn, 'groupname')  # verifies that the group exists
   group.add_user(user)  # may also just be the username!
   group.get_members()  # returns a list with the User element


.. _guide_error-handling:

Error handling
--------------

Like all RestAuth client libraries, the python client library features many custom exceptions with a
multi-leveled inheritance model. This allows you to handle problems with whatever granularity you
want.

Since the Python library is the reference implementation, many other libraries feature a similar or
even identical Exception class-hierarchy. Since both the `RestAuth server reference implementation
<https://server.restauth.net>`_ and RestAuthClient use the same exceptions for error handling, most
exceptions are located in :py:mod:`RestAuthCommon.error`. For an introduction on how to use those
exceptions, please see the `error handling chapter <https://common.restauth.net/error.html>`_ in the
RestAuthCommon documentation.

RestAuthClient provides a view additional exceptions that only make sense at the client side. Please
see the :py:mod:`error module <RestAuthClient.error>` for more documentation.

Upgrade
-------

0.6.2
_____

Many module and class names changed for consistency. Wrappers for the old class
names are provided, so you shouldn't run into immediate problems. It is non the
less advised to upgrade to the new module paths::

   # old imports:
   #from RestAuthClient.restauth_user import User
   #from RestAuthClient.group import Group

   # new imports:
   from RestAuthClient.user import RestAuthUser
   from RestAuthClient.group import RestAuthGroup

   # factory functions are now class functions, so instead of:
   #restauth_user.get(...)

   # ... use new class-level functions:
   RestAuthUser.get(...)

