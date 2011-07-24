group - group handling
======================

The **group** module includes all code relevant to group management. Just like the
:doc:`restauth_user <restauth_user>` module, the module contains factory methods (:py:meth:`~.group.get`,
:py:meth:`~.group.get_all` or :py:meth:`~.group.create`) and the :py:class:`.Group` class that
offers an interface for managing a group.

Just like with users, it is recommended to instantiate a :py:class:`.Group` object directly if
performance is critical. Please see the :doc:`restauth_user <restauth_user>` module for an analogous
example.

API documentation
-----------------

.. automodule:: RestAuthClient.group
        :members:
