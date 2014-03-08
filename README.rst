RestAuthClient is the Python reference implementation for RestAuth_, a protocol
providing shared authentication, authorization and preferences.

Requirements
============

**RestAuthClient** requires nothing but RestAuthCommon_ and any library
required by any content handler you may use. **RestAuthClient** runs with
Python2.6+ and Python3.2+.

Installation
============

Full installation instructions are provided on the `homepage
<https://python.restauth.net>`_.

If you use pip, you can install RestAuthClient with

```bash
pip install RestAuthClient
```

If you want to install Debian/Ubuntu packages, simple do:

```bash
wget -O - http://apt.fsinf.at/keys/apt-repository@fsinf.at | apt-key add -
echo deb http://apt.fsinf.at <dist> restauth > /etc/apt/sources.list.d/restauth.list
apt-get update
apt-get install python-restauth python3-restauth
```

Getting started
===============

Please see the guide_.

.. _RestAuthCommon: https://common.restauth.net
.. _guide: https://python.restauth.net/intro.html
