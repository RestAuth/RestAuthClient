common - Common code used by other classes
==========================================

.. automodule:: RestAuthClient.common
      :members:

SSL options
-----------
.. Note:: This features requires that you use python 3.2 or later.

A :py:class:`RestAuthConnection` instance also has the property 'context', which is an
:py:class:`ssl.SSLContext` instance used for SSL connections. You can directly call methods on this
instance if you want to set different SSL options. By default, :attr:`~ssl.SSLContext.verify_mode` is set
to :data:`~ssl.CERT_REQUIRED`.