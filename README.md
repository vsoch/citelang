# CiteLang

[![PyPI version](https://badge.fury.io/py/citelang.svg)](https://badge.fury.io/py/citelang)

Welcome to CiteLang! CiteLang provides methods and graph-based modeling to study software
ecosystems. You can use CiteLang for your research, or a provided tool to generate
software graph artifacts, including (but not limited to):

1. Generate basic software credit trees (citelang graph, badge, or markdown credit)
2. Give credit accounting for dependencies! (see [software-credit.md](software-credit.md))
3. Actions (automation) for the above!

For the examples above, we aren't using DOIs! A manually crafted identifier that a human has to remember to generate,
in addition to a publication or release, is too much work for people to reasonably do. As research
software engineers we also want to move away from the traditional "be valued like an academic" model.
We are getting software metadata and a reference to an identifier via a package manager. This means
that when you publish your software, you should publish it to an appropriate package manager.

## Getting Started 

If you want to use CiteLang as an analysis library, jump into the mode detailed ⭐️ [Documentation](https://vsoch.github.io/citelang) ⭐️ 
or look specifically at the [Python API](https://vsoch.github.io/citelang/getting_started/user-guide.html#python).
As an example analysis, the [RSEPedia Software Ecosystem](https://rseng.github.io/rsepedia-analysis/) is a completed automated setup that parses and summarizes dependencies across the [Research Software Encyclopedia](https://rseng.github.io/software) weekly, and it's powered by CiteLang! You can do similar analyses or build your own tools using CiteLang. We will provide a small summary of the tools available here.

### Badges

CiteLang [**Badges**](https://vsoch.github.io/citelang/getting_started/user-guide.html#badge) can show an entire credit tree
for a project:

![https://raw.githubusercontent.com/vsoch/citelang/main/docs/assets/img/pypi-citelang.png](https://raw.githubusercontent.com/vsoch/citelang/main/docs/assets/img/pypi-citelang.png)

or can be generated to be interactive web interfaces as [shown here](https://vsoch.github.io/citelang/_static/example/badge/treemap/index.html).

![https://raw.githubusercontent.com/vsoch/citelang/main/docs/getting_started/img/badge.png](https://raw.githubusercontent.com/vsoch/citelang/main/docs/getting_started/img/badge.png)

See the [badge](https://vsoch.github.io/citelang/_static/example/badge/treemap/index.html) documentation for more examples
of customizing the look, or level of abstraction. You can automatically generate or update
a badge for your repository using the provided [GitHub Action](https://vsoch.github.io/citelang/getting_started/user-guide.html#badge-github-action).

### Credit and Graph

If you want to visually show dependency graphs, using [**Credit**](https://vsoch.github.io/citelang/getting_started/user-guide.html#credit)
will print this to the console, and optionally in json if you want just the data. With the [**Graph**](https://vsoch.github.io/citelang/getting_started/user-guide.html#graph) command you can render different kinds of pretty graphs (or data formats dot, cypher, gexf) using this same data.

![https://raw.githubusercontent.com/vsoch/citelang/main/examples/console/citelang-console-pypi.png](https://raw.githubusercontent.com/vsoch/citelang/main/examples/console/citelang-console-pypi.png)
![https://raw.githubusercontent.com/vsoch/citelang/main/examples/cypher/graph.png](https://raw.githubusercontent.com/vsoch/citelang/main/examples/cypher/graph.png)

### Contributions

CiteLang has a [**Contrib**](https://vsoch.github.io/citelang/getting_started/user-guide.html#contrib) command and underlying
API that can dig into your git history and look at contributions based on lines. You can read a complete write-up
and see examples [in this blog post](https://vsoch.github.io/2022/citelang-contrib/#citelang-contrib). It is currently being used
by the SingularityCE project to say thank you to contributors!

[![asciicast](https://asciinema.org/a/486073.svg)](https://asciinema.org/a/486073?speed=2)

If you want to generate data programatically, we provide [A GitHub action](https://vsoch.github.io/citelang/getting_started/user-guide.html#contribute-github-action).


### Render and Generate

The functionality that originally derived the name - a "markdown syntax for citations" means that we can start from a [markdown paper](https://github.com/vsoch/citelang/blob/main/examples/pre-render.md) that has some number of CiteLang formatted references, and result in a [rendered paper](https://github.com/vsoch/citelang/blob/main/examples/post-render.md) that includes a credit table. This is done with the [**Render**](https://vsoch.github.io/citelang/getting_started/user-guide.html#render) command, or you can just output a table into its own markdown file with [**Generate**](https://vsoch.github.io/citelang/getting_started/user-guide.html#gen-generate). We provide [an example here](https://github.com/vsoch/citelang/blob/main/software-credit.md) and also provide a [GitHub action](https://vsoch.github.io/citelang/getting_started/user-guide.html#generate-github-action) for you to generate this for your own repository.



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
