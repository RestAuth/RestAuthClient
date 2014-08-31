user - user handling
====================

The **user** module includes all code related to user management. You can use one of the factory
methods (:py:meth:`~.RestAuthUser.get`, :py:meth:`~.RestAuthUser.get_all` or
:py:meth:`~.RestAuthUser.create`) to retreive an instance or a list of instances of the
:py:class:`.RestAuthUser` class.

The factory methods make sure that the :py:class:`.RestAuthUser` object used represents a user that
actually exists in the RestAuth service by verifying the existance for returning the respective
instance(s).  If performance is critical, however, it is better to instantiate an instance
directly, perform the desired operations on that object and catch the case of a non-existing user
with an exception handler.


.. code-block:: python

   from RestAuthClient.common import RestAuthClient
   from RestAuthClient.user import RestAuthUser
   conn = RestAuthConnection('https://auth.example.com', 'service', 'password')

   # this is two requests:
   user = RestAuthUser.get('username') # does one request
   user.verify_password('password')

   # this is just one request:
   user = RestAuthUser('username') # does no request
   user.verify_password('password')

API documentation
-----------------

.. automodule:: RestAuthClient.user
   :members:
