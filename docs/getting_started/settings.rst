.. _getting_started-settings:

========
Settings
========

Most defaults should work without changing, however you will likely want to customize
settings if you want to customize your cache location or similar.

Updating Settings
=================

To change defaults you can either edit the settings.yml file in the installation directory
at ``citelang/settings.yml`` or create a user-specific configuration by doing:


.. code-block:: console

    $ citelang config userinit
    Created user settings file /home/vanessa/.citelang/settings.yml


You can then change a setting, such as the cache directory:


.. code-block:: console

    $ citelang config set cache_dir:/tmp/cache


Settings Table
==============

The following variables can be configured in your user settings:

.. list-table:: Title
   :widths: 25 65 10
   :header-rows: 1

   * - Name
     - Description
     - Default
   * - disable_cache
     - Disable caching packages and managers
     - false
   * - disable_memory_cache
     - Disable caching package managers and packages to memory during a session
     - false
   * - cache_dir
     - This is in user home in .citelang by default
     - $citelang_home/cache
