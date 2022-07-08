.. _getting_started-installation:

============
Installation
============

Install CiteLang
----------------

Install citelang from pypi:

.. code-block:: console

    $ pip install citelang


or development from the code:

.. code-block:: console

    $ git clone https://github.com/vsoch/citelang
    $ cd citelang
    $ pip install -e .

Testing
-------

To see full details about how citelang is tested, see ``.github/workflows``. To quickly test the
library locally, you'll need to do a full install (badge generation libraries included) and bs4 for testing GitHub dependencies:

.. code-block:: console

   $ pip install -e .[all]
   $ pip install bs4

It's recommended (but not required) for tests that you have a `libraries.io <https://libraries.io>`_ API key exported. If you don't, the client will sleep while the API limit is exceeded (the test will appear to pause).

.. code-block:: console

     export CITELANG_LIBRARIES_KEY=xxxxxxxxxxxxxxx

And then after that, and when you have citelang on your path:

.. code-block:: console

    $ cd citelang/tests
    $ /bin/bash test_client.sh
    $ pytest test_*.py

Next check out the :ref:`getting_started-user-guide` pages for more detail to use the library.
