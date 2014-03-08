RestAuthClient is the Python reference implementation for RestAuth_, a protocol
providing shared authentication, authorization and preferences.

Requirements
============

**RestAuthClient** runs with Python2.6+ and Python3.2+.

**RestAuthClient** requires no special libraries but RestAuthCommon_ and any
library required by any content handler you use.


Installation
============

Full installation instructions are provided on the `homepage
<https://python.restauth.net>`_.

If you use pip, you can install RestAuthClient with::

   pip install RestAuthClient

If you want to install Debian/Ubuntu packages, simple do::

   wget -O - http://apt.fsinf.at/keys/apt-repository@fsinf.at | apt-key add -
   echo deb http://apt.fsinf.at <dist> restauth > /etc/apt/sources.list.d/restauth.list
   apt-get update
   apt-get install python-restauth python3-restauth

Getting started
===============

Please see our guide_.

.. _RestAuth: https://restauth.net
.. _RestAuthCommon: https://common.restauth.net
.. _guide: https://python.restauth.net/intro.html
