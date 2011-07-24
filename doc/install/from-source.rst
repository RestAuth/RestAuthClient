Installation from source
========================

Requirements
------------

RestAuthClient is written as a *bleeding edge* project and thus requires relatively new software
versions.

* `Python 2.6 <http://www.python.org/>`_ or later
* `RestAuthCommon <https://redmine.fsinf.at/projects/restauthcommon>`_
* The `mimeparse <https://code.google.com/p/mimeparse/>`_ module is required by RestAuthCommon

Get source
----------

From git
++++++++

This project is developed on `git.fsinf.at <https://git.fsinf.at/>`_. You can view the source code
at `git.fsinf.at/restauth/python  <https://git.fsinf.at/restauth/python>`_. To clone the
repository to a directory named "RestAuthClient", simply do:

.. code-block:: bash

   git clone http://git.fsinf.at/restauth/python.git RestAuthClient

Older versions are marked as tags. You can view available tags with :command:`git tag -l`. You can
use any of those versions with :command:`git checkout`, for example :command:`git checkout 1.0`.
To move back to the newest version, use :command:`git checkout master`.

If you ever want to update the source code, just use:

.. code-block:: bash

   python setup.py clean
   git pull
   
... and do the same as if you where
:ref:`doing a new installation <install_from-source_installation>`.

Official releases
+++++++++++++++++

There are no "official releases* yet, hence no tarballs to download ;-).

.. _install_from-source_installation:

Installation
------------

Installation itself is very easy. Just go to the directory where your source is located
("RestAuthClient" in the above example) and just run:

.. code-block:: bash

   python setup.py build
   python setup.py install

.. NOTE:: On most systems, the latter command needs to run with superuser privileges.


You can verify that the installation worked by running this command from your home directory:

.. code-block:: bash

   cd
   python -c "import RestAuthClient"

This will throw an ImportError if RestAuthClient was not installed successfully.


Run tests
---------

.. WARNING:: Running the test-suite or generating a test coverage support will **remove all data**
   from the running RestAuth server. Do not perform these tests on a live installation.

RestAuthClient features an extensive test suite. Since it implements a network protocol, the library
requires a RestAuth server to run on ``http://[::1]:8000`` that has the service ``vowi`` with the
password ``vowi`` preconfigured. The `RestAuth server <https://server.restauth.net>`_ contains the
script ``test.sh`` in its source code to simply start a server and add the expected service. 

After you started the server, you can run test-suite using:

.. code-block:: bash

   python setup.py test

Test coverage
+++++++++++++

You can also generate a test coverage report using `coverage.py
<http://nedbatchelder.com/code/coverage/>`_ using:

.. code-block:: bash
   
   python setup.py coverage

By default, a pretty coverage report will go to doc/coverage/.

Build documentation
-------------------

To generate the most recent documentation (the newest version of the document you're currently
reading), just run:

.. code-block:: bash

   python setup.py build_doc