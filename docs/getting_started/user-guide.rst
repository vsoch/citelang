.. _getting_started-user-guide:

==========
User Guide
==========


Welcome to CiteLang! This is the first markdown syntax for citing software. Importantly,
when you use CiteLang to reference software.

1. Generate basic software credit trees
2. Give credit accounting for dependencies!

No - we aren't using DOIs! A manually crafted identifier that a human has to remember to generate,
in addition to a publication or release, is too much work for people to reasonably do. As research
software engineers we also want to move away from the traditional "be valued like an academic" model.
We are getting software metadata and a reference to an identifier via a package manager. This means
that when you publish your software, you should publish it to an appropriate package manager.
Please `let us know <https://github.com/vsoch/citelang/issues>`_ if you have a questions, 
find a bug, or want to request a feature! This is an open source project and we are 
eager for your contribution. 🎉️

.. _getting_started-user-guide-usage:

*****
Usage
*****

Once you have ``citelang`` installed (:ref:`getting_started-installation`) you
can use citelang either from the command line, or from within Python.

.. _getting_started-user-guide-usage-client:


Credentials
===========

CiteLang will require a libraries.io token, so you should `login <https://libraries.io/>`_ (it works with 
GitHub and other easy OAuth2 that don't require permissions beyond your email) and then
go to the top right -> Settings -> API Key.

You'll want to export this in the environment:

.. code-block:: console

    export CITELANG_LIBRARIES_KEY=xxxxxxxxxxxxxxxxxxxxxxxxx

If you use the GitHub package type, it's recommended to export a GitHub token too.

.. code-block:: console

    export GITHUB_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxx

********
Commands
********

The following commands are available.

Package Managers
================

Let's find package managers supported.

.. code-block:: console

    $ citelang list

This gives us the listing of package managers that we can interact with. Since by default
we create a cache of results (to not use our token ratelimit whenever possible) after calling
this endpoint you'll find packages cached in your citelang home!

.. code-block:: console

    $ tree ~/.citelang/
    /home/vanessa/.citelang/
    ├── cache
    │   └── package_managers.json
    └── settings.yml

This means if you make the call again, it will load data from here instead of making an API call.
Note that there are actually two caches - the filesystem and memory cache. These are discussed in the
config section. You can disable using or setting the cache for any command as follows:


.. code-block:: console

    $ citeling list --no-cache

Package
=======

To get metadata for a package, or from the command line, to list versions available:

.. code-block:: console

    $ citelang package pypi requests

image:: img/package-requests.png


Dependencies
============

You can ask to see package dependencies:

.. code-block:: console

    $ citelang deps pypi requests


If you don't provide a version, the latest will be used (retrieved from the package).

.. code-block:: console
    
    $ citelang deps pypi requests@2.27.1

image:: img/requests-deps.png


Config
------

You don't technically need to do any custom configuration. However, if you want to make
your own user-specific settings file:

.. code-block:: console

    $ citelang config inituser


You can also edit the default config in [citelang/settings.yml](citelang/settings.yml)
if you control the install. We will be adding a table of settings when we add official
documentation. For now, let's talk about specific variables.


disable_cache
-------------

This defaults to false, meaning we aren't disabling the cache. Not disabling the cache
means we can cache different results in your citelang home. We do this to minimize API calls.
The exception is for when you ask for a package without a version. Since we cannot
be sure what the latest version is, we need to check again.

disable_memory_cache
--------------------

Akin to the filesystem, given that you are using a client in a session (whether directly
in Python or via a command provided by citelang) we will cache results in memory. E.g.,
if you are asking for multiple packages, we check first that you are asking for a valid
manager. When we cache the list of managers available, this is possible without an extra
API call.


Cache
=====

Citelng includes a cache command group for viewing or clearing your filesystem cache.

.. code-block:: console

    $ citelang cache
    /home/vanessa/.citelang/cache
    
    
Or list what's in it!

.. code-block:: console
    
    $ tree $(citelang cache)


And finally, clear it. You'll get a confirmation prompt first.

.. code-block:: console

    $ citelang cache --clear
    Are you sure you want to clear the cache? yes


Credit
======

To create a simple citation credit calculation, you can do:

.. code-block:: console

    $ citelang credit pypi requests


By default, we will split the credit graph until:

 1. if set, we reach a threshold N of packages added (`--max-depth`)
 2. if set, we reach a total number of unique dependencies added (`--max-deps`)
 3. we reach a threshold that is smaller than our minimum credit (`--min-credit`) 

It's up to you to set the first two cases (they default to None, meaning unset) and
we always only go up to a minimum threshold (or when there are no more dependencies to allocate).
Note that first time you do it, you'll see the endpoints being hit (they aren't cached yet):

.. code-block:: console

    $ citelang credit pypi requests
    GET https://libraries.io/api/platforms
    GET https://libraries.io/api/pypi/requests
    GET https://libraries.io/api/pypi/requests/2.27.1/dependencies
    GET https://libraries.io/api/pypi/win-inet-pton
    GET https://libraries.io/api/pypi/win-inet-pton/1.1.0/dependencies
    GET https://libraries.io/api/pypi/PySocks
    GET https://libraries.io/api/pypi/PySocks/1.7.1/dependencies
    GET https://libraries.io/api/pypi/charset-normalizer
    GET https://libraries.io/api/pypi/charset-normalizer/2.0.12/dependencies
    GET https://libraries.io/api/pypi/idna
    GET https://libraries.io/api/pypi/idna/0.1/dependencies
    GET https://libraries.io/api/pypi/chardet
    GET https://libraries.io/api/pypi/chardet/4.0.0/dependencies
    GET https://libraries.io/api/pypi/certifi
    GET https://libraries.io/api/pypi/certifi/2015.4.28/dependencies
    GET https://libraries.io/api/pypi/urllib3
    GET https://libraries.io/api/pypi/urllib3/1.26.8/dependencies

And then you'll get the credit score:


.. code-block:: console

    $ citelang credit pypi requests 
                  requests: 0.5
               win-inet-pton: 0.071
                     PySocks: 0.071
          charset-normalizer: 0.036
                    unicodedata2: 0.036
                        idna: 0.071
                     chardet: 0.071
                     certifi: 0.071
                     urllib3: 0.071
    total: 1.0


The default "minimum credit" (to determine when we stop parsing) is 0.01. 
You can also try changing this value!

.. code-block:: console

    $ citelang credit pypi requests --min-credit 0.005
                  requests: 0.5
               win-inet-pton: 0.071
                     PySocks: 0.071
          charset-normalizer: 0.036
                    unicodedata2: 0.036
                        idna: 0.071
                     chardet: 0.071
                     certifi: 0.071
                     urllib3: 0.036
                         PySocks: 0.005
                       ipaddress: 0.005
                         certifi: 0.005
                            idna: 0.005
                    cryptography: 0.005
                       pyOpenSSL: 0.005
                        brotlipy: 0.005
    total: 1.0


By default, the ``--max-depth`` and ``--map-deps`` are unset so we don't stop parsing based on some
maximum depth or number of dependencies. You can try setting these values as well.

Graph
=====

To create a simple citation graph, you can do:

.. code-block:: console

    $ citelang graph pypi requests


This will print a (much prettier) rendering of the graph to the console! Here is for pypi:

.. image:: https://raw.githubusercontent.com/vsoch/citelang/main/examples/console/citelang-console-pypi.png


And citelang has custom package parsers, meaning we can add package managers that aren't in libraries.io!
Here is spack:


.. code-block:: console

    $ citelang graph spack caliper


.. image:: https://raw.githubusercontent.com/vsoch/citelang/main/examples/console/citelang-console-spack.png

And GitHub.


.. code-block:: console

    $ citelang graph github singularityhub/singularity-hpc

.. image:: https://raw.githubusercontent.com/vsoch/citelang/main/examples/console/citelang-console-github.png

GitHub is a bit of a deviant parser because we use the dendency graph that GitHub has found in your repository.
If you have a non-traditional way of defining deps (e.g., singularity-cli above writes them into a version.py that gets piped into setup.py) they won't show up. Also note that when you cite GitHub, we are giving credit to ALL the software you use for your setup, including documentation and CI. Here is a more traditional GitHub repository
that has a detectable file.


Dot
---

To generate (and then render a dot graph):

.. code-block:: console

    $ citelang graph pypi requests --fmt dot > examples/dot/graph.dot
    $ dot -Tpng < examples/dot/graph.dot > examples/dot/graph.png
    $ dot -Tsvg < examples/dot/graph.dot > examples/dot/graph.svg

Cypher
------

Cypher is the query format for Neo4j, the graph database.

.. code-block:: console
    
    $ citelang graph pypi requests --fmt cypher

    CREATE (tlolycos:PACKAGE {name: 'requests (0.5)', label: 'tlolycos'}),
    (jgaoitav:PACKAGE {name: 'win-inet-pton (0.071)', label: 'jgaoitav'}),
    (jijibmow:PACKAGE {name: 'PySocks (0.071)', label: 'jijibmow'}),
    (gotbtadg:PACKAGE {name: 'charset-normalizer (0.036)', label: 'gotbtadg'}),
    (lflybqsc:PACKAGE {name: 'idna (0.071)', label: 'lflybqsc'}),
    (kitlrsbz:PACKAGE {name: 'chardet (0.071)', label: 'kitlrsbz'}),
    (gnveurko:PACKAGE {name: 'certifi (0.071)', label: 'gnveurko'}),
    (eoikqvix:PACKAGE {name: 'urllib3 (0.071)', label: 'eoikqvix'}),
    (kvccvkva:PACKAGE {name: 'unicodedata2 (0.036)', label: 'kvccvkva'}),
    (tlolycos)-[:DEPENDSON]->(jgaoitav),
    (tlolycos)-[:DEPENDSON]->(jijibmow),
    (tlolycos)-[:DEPENDSON]->(gotbtadg),
    (tlolycos)-[:DEPENDSON]->(lflybqsc),
    (tlolycos)-[:DEPENDSON]->(kitlrsbz),
    (tlolycos)-[:DEPENDSON]->(gnveurko),
    (tlolycos)-[:DEPENDSON]->(eoikqvix),
    (gotbtadg)-[:DEPENDSON]->(kvccvkva);
    
What you are seeing above is a definition of node and relationships. You can pipe to file:


.. code-block:: console

    $ citelang graph pypi requests --fmt cypher > examples/cypher/graph.cypher


If you test the output in the [Neo4J sandbox](https://sandbox.neo4j.com/) by first running the code to generate nodes and then doing:

.. code-block:: console

    MATCH (n) RETURN (n)


You should see:

.. image:: https://raw.githubusercontent.com/vsoch/citelang/main/examples/cypher/graph.png

From within Python you can do:

.. code-block:: console

    from citelang.main import Client
    client = Client()
    client.graph(manager="pypi", name="requests", fmt="cypher")
    
    
Gexf (NetworkX)
---------------

If you want to use networkX or Gephi or a `viewer <https://github.com/raphv/gexf-js>`_ you can generate output as follows:

.. code-block:: console

    $ citelang graph pypi requests --fmt gexf
    $ citelang graph pypi requests --fmt gexf > examples/gexf/graph.xml

To use the viewer, you’ll first need to import into Gephi so the nodes have added spatial information. Without this information, you won’t see them in the UI. You can then do the following:

.. code-block:: console

    $ here=$PWD
    $ cd /tmp
    $ git clone https://github.com/raphv/gexf-js
    $ cd gexf-js


The file we generated above, we copy over the example so we don't have to edit config.js

.. code-block:: console

    $ cp $here/examples/gexf/graph.xml miserables.gexf


And then run the server!

.. code-block:: console

    python -m http.server 9999


As an alternative, networkx can also read in the gexf file:

.. code-block:: python

    import matplotlib.pyplot as plt
    import networkx as nx

    graph = nx.read_gexf('examples/gexf/graph.xml')

    nx.draw(graph, with_labels=True, font_weight='bold')
    plt.show()


That should generate `examples/gexf/graph.xml <https://raw.githubusercontent.com/vsoch/citelang/main/examples/gexf/graph.xml>`_.


Badge
=====

A badge is an interactive svg (meaning it will typically output an index.html file for you to include
somewhere) for a user to interactively explore your dependency tree. We took inspiration from
the periodic table of elements, meaning that the top layer looks like a single element, and clicking
allows you to explore the nested inner tables.


.. code-block:: console

    $ citelang badge pypi requests

or for more depth in your badge (and to save to a custom output file):


.. code-block:: console

    $ citelang badge pypi requests --min-credit 0.001 --outfile index.html
    Saving to index.html...
    Result saved to index.html

Here is the current example badge - you can click around to explore it!

image:: img/badge.png

Or see the `interactive version here <../_static/example/badge/index.html>`_.

The badge design is still being developed - for example it would be good to have
a smaller version, or a static one. If you have ideas or inspiration please
open an issue!

Render
======

This command will support rendering:

1. an entire markdown file with software references 
2. a grouping / list of software references
3. a page with multiple badges?

and create a citation summary table that can represent shared credit across your dependencies, weighted equally (by default)
per package. As an example, let's say we start with _`this markdown file <https://github.com/vsoch/citelang/blob/main/examples/paper.md>`_ .
You'll notice there are software references formatted as follows:

.. code-block:: markdown

    @apt{name=singularity-container, version=3.8.2}
    @pypi{name=singularity-hpc}
    @github{name=autamus/registry}
    @github{name=spack/spack, release=0.17}.

And it ends in a References section, under which we've defined a start and ending tag (in html) for citelang.

.. code-block:: markdown

    <!--citelang start-->
    <!--citelang end-->

Then to render the citation table into the file:


.. code-block:: console

   $ citelang render examples/paper.md


This will print the result to the screen! To save to output file (overwrite the same file or write to a different file):


.. code-block:: console

   $ citelang render examples/paper.md --outfile examples/paper-render.md

You can see an `example rendering here <https://github.com/vsoch/citelang/blob/main/examples/paper-render.md>`_.
We are thinking about also generating a graphic to embed somewhere, and associated actions for both.
Let us know if you have ideas!

******
Python
******

You can do all of the same interactions from within Python! And indeed if you want
to do some kind of analysis or custom parsing this is the recommended approach.
For all cases from within Python, after exporing the token, we need to create a client.

.. code-block:: python

    from citelang.main import Client
    client = Client()
    
You can optionally provide a custom settings file:

.. code-block:: python

    client = Client(settings_file="settings.yml")


Now let's get our list of package managers:

.. code-block:: python

    result = client.package_managers()


The raw data will be here on the results object:

.. code-block:: python

    result.data


And this is how we print to the terminal

.. code-block:: python

    result.table()


Let's say you ran this, and you wanted to retrieve it again! Given that ``disable_cache`` in your settings
is not set to True, you can call the function again and the data returned will be from the cache.
You can also ask for it verbatim:

.. code-block:: python

    client.package_managers()

or 

.. code-block:: python

    client.get_cache('package_managers')

    {'name': 'Inqlude',
     'project_count': 228,
     'homepage': 'https://inqlude.org/',
     'color': '#f34b7d',
     'default_language': 'C++'}]


To get metadata for a package:

.. code-block:: python
    
    client.package(manager="pypi", name="requests")

Or to ask for dependencies:

.. code-block:: python

    client.dependencies(manager="pypi", name="requests")

Without a version, we will grab the latest. Otherwise we use the version provided.


**************************
Frequently Asked Questions
**************************

Why don't the trees print versions?
===================================

The current thinking is that when I give credit to software, I'm not caring so much about the version.
The goal of this isn't reproducibility, but rather to say "for this software package, here are the dependencies and credits to give for each." Given a version (which will default to latest) this will mean a particular
set of dependencies, but it's not something we require reproducing, especially because we choose a threshold (number of dependencies, a credit minimum threshold, or depth) to cut our search. The only data we care about is preserving a representation of how to give credit after we do a search.

Why don't the trees show package managers?
==========================================

In truth we probably should, because looking at a credit graph later you need to know the manager
used to derive the graph (e.g., some packages can be present in multiple package managers!) 
I haven't added this yet. 


This library is under development and we will have more documentation coming soon!