**RestAuthClient** is the reference client implementation, for RestAuth_,
written in Python. RestAuth is a protocol providing shared authentication,
authorization and preferences.

Requirements
============

**RestAuthClient** works with Python2.7+ and Python3.2+.

**RestAuthClient** requires no special libraries but RestAuthCommon_ and any
library required by any content handler you use. ``pip install RestAuthClient``
automatically installs RestAuthCommon_.

Installation
============

Full installation instructions are provided on the `homepage
<https://python.restauth.net>`_.

If you use pip, you can install **RestAuthClient** with::

   pip install RestAuthClient

If you want to install Debian/Ubuntu packages, simple do (Replace **<dist>**
with your distribution)::

   apt-get install apt-transport-https
   wget -O - https://apt.restauth.net/gpg-key | apt-key add -
   echo deb https://apt.restauth.net <dist> restauth > /etc/apt/sources.list.d/restauth.list
   apt-get update
   apt-get install python-restauth python3-restauth

Getting started
===============

Please see our guide_.

.. _RestAuth: https://restauth.net
.. _RestAuthCommon: https://common.restauth.net
.. _guide: https://python.restauth.net/intro.html
