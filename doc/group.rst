group - group handling
======================

The **group** module includes all code relevant to group management. Just like the :doc:`user
<user>` module, the module contains factory methods (:py:meth:`~.RestAuthGroup.get`,
:py:meth:`~.RestAuthGroup.get_all` or :py:meth:`~.RestAuthGroup.create`) and the
:py:class:`.RestAuthGroup` class that offers an interface for managing a group.

Just like with users, it is recommended to instantiate a :py:class:`.RestAuthGroup` object directly
if performance is critical. Please see the :doc:`user <user>` module for an analogous example.

API documentation
-----------------

.. automodule:: RestAuthClient.group
        :members:
