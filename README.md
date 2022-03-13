# CiteLang

[![PyPI version](https://badge.fury.io/py/citelang.svg)](https://badge.fury.io/py/citelang)

Welcome to CiteLang! This is the first markdown syntax for citing software. Importantly,
when you use CiteLang to reference software.

1. Generate basic software credit trees
2. Give credit accounting for dependencies!

No - we aren't using DOIs! A manually crafted identifier that a human has to remember to generate,
in addition to a publication or release, is too much work for people to reasonably do. As research
software engineers we also want to move away from the traditional "be valued like an academic" model.
We are getting software metadata and a reference to an identifier via a package manager. This means
that when you publish your software, you should publish it to an appropriate package manager.

## Quick Start

CiteLang will require a libraries.io token, so you should [login](https://libraries.io/) (it works with 
GitHub and other easy OAuth2 that don't require permissions beyond your email) and then
go to the top right -> Settings -> API Key.

You'll want to export this in the environment:

```bash
export CITELANG_LIBRARIES_KEY=xxxxxxxxxxxxxxxxxxxxxxxxx
```

And of course you will need to install it, either from pip or the repository.

```bash
$ pip install citelang
```
or

```bash
$ git clone https://github.com/vsoch/citelang
$ cd citelang
$ pip install -e .
```

This will place an executable `citelang` in your directory. For the commands below,
we will show interactions using the command line client and Python API.

## Usage

For all cases from within Python, after exporing the token, we need to create a client.

```python
from citelang.main import Client
client = Client()
```

### Package Managers

Let's find package managers supported.

```python
$ result = client.package_managers()
$ result.data

# This is how we print to the terminal
$ result.table()
```

Let's say you ran this, and you wanted to retrieve it again! Given that `disable_cache` in your settings
is not set to True, you can call the function again and the data returned will be from the cache.
You can also ask for it verbatim:

```python
$ cli.get_cache('package_managers')
...
 {'name': 'Inqlude',
  'project_count': 228,
  'homepage': 'https://inqlude.org/',
  'color': '#f34b7d',
  'default_language': 'C++'}]
```

And from the command line:

```bash
$ citelang list
```

This gives us the listing of package managers that we can interact with. Since by default
we create a cache of results (to not use our token ratelimit whenever possible) after calling
this endpoint you'll find packages cached in your citelang home!

```bash
$ tree ~/.citelang/
/home/vanessa/.citelang/
├── cache
│   └── package_managers.json
└── settings.yml
```

This means if you make the call again, it will load data from here instead of making an API call.
Note that there are actually two caches - the filesystem and memory cache. These are discussed in the
config section.


### Package

```python
$ client.package(manager="pypi", name="requests")
```

And from the command line:

```bash
$ citelang package pypi requests
```

Or with a version:

```bash
$ citelang package pypi requests@2.27.1
```


### Config

You don't technically need to do any custom configuration. However, if you want to make
your own user-specific settings file:

```bash
$ citelang config inituser
```

You can also edit the default config in [citelang/settings.yml](citelang/settings.yml)
if you control the install. We will be adding a table of settings when we add official
documentation. For now, let's talk about specific variables.

### disable_cache

This defaults to false, meaning we aren't disabling the cache. Not disabling the cache
means we can cache different results in your citelang home. We do this to minimize API calls.
The exception is for when you ask for a package without a version. Since we cannot
be sure what the latest version is, we need to check again.

### disable_memory_cache

Akin to the filesystem, given that you are using a client in a session (whether directly
in Python or via a command provided by citelang) we will cache results in memory. E.g.,
if you are asking for multiple packages, we check first that you are asking for a valid
manager. When we cache the list of managers available, this is possible without an extra
API call.


## TODO

 - add citlang cache command group
 - create documentation, settings table
 - add support for version

## Contributors

We use the [all-contributors](https://github.com/all-contributors/all-contributors) 
tool to generate a contributors graphic below.

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://vsoch.github.io"><img src="https://avatars.githubusercontent.com/u/814322?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Vanessasaurus</b></sub></a><br /><a href="https://github.com/vsoch/citelang/commits?author=vsoch" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## License

This code is licensed under the MPL 2.0 [LICENSE](LICENSE).
