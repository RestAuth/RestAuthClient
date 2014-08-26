Installation on Debian/Ubuntu
=============================

The RestAuth project provides APT repositories for all software it maintains. Repositories are
available for all distributions that are currently maintained by the Debian
project and Canonical.

Adding our APT repository
-------------------------

To add the repositories, simply add this line to your :file:`/etc/apt/sources.list` file::

   echo "deb https://apt.fsinf.at <DIST> restauth" > /etc/apt/sources.list.d/restauth.list

... where ``<DIST>`` is any of the supported distributions. If you are unsure of your
distribution, you can run the following in your terminal::

   lsb_release -sc

You can also read the WikiPedia pages for `Ubuntu
<https://en.wikipedia.org/wiki/List_of_Ubuntu_releases#Table_of_versions>`_ and `Debian
<https://en.wikipedia.org/wiki/Debian#Release_history>`_ to see how they map to your installation.
You can also check the `APT repository itself <https://apt.fsinf.at/dists>`_ for a list of available
distributions (don't forget to check the 'Last modified' timestamp!).

Once you added the repository, you have to install the fsinf GPG keyring used for signing the
repositories, so you won't get any warnings when updating. You can either install the
``fsinf-keyring`` package using:

.. code-block:: bash

   apt-get install apt-transport-https
   apt-get update
   apt-get install fsinf-keyring
   apt-get update

or download and add the key directly using:

.. code-block:: bash

   wget -O - https://apt.fsinf.at/gpg-key | apt-key add -

Install RestAuthClient
----------------------

Once you have added the repositories, installing RestAuthClient is as simple as

.. code-block:: bash

   apt-get install python-restauth

or, if you use Python 3::

   apt-get install python3-restauth
