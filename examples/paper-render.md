# Summary

Portability and reproducibility of complex software stacks is essential for researchers to perform their work. High Performance Computing (HPC) environments add another level of complexity, where possibly conflicting dependencies must co-exist. Although container technologies like Singularity @conda{name=singularity} make it possible to "bring your own environment," without any form of central strategy to manage containers, researchers who seek reproducibility via using containers are tasked with managing their own container collection, often not taking care to ensure that a particular digest or version is used. The reproducibility of the work is at risk, as they cannot easily install and use containers, nor can they share their software with others.

Singularity Registry HPC (shpc) @pypi{name=singularity-hpc} is the first of its kind to provide an easy means for a researcher to add their research software for sharing and collaboration with other researchers to an existing collection of over 200 popular scientific libraries @github{name=autamus/registry} @github{name=spack/spack, release=0.17}. The software installs containers as environment modules that are easy to use and read docuementation for, and exposes aliases for commands in the container that the researcher can add to their pipeline without thinking about complex interactions with a container. The simple addition of an entry to the registry maintained by shpc comes down to adding a yaml file, and after doing this, another researcher can easily install the same software, down to the digest, to reproduce the original work.

# References

<!--citelang start-->
|Manager|Name|Credit|
|-------|----|------|
|conda|[singularity](https://singularity.hpcng.org)|0.12|
|pypi|[singularity-hpc](https://github.com/singularityhub/singularity-hpc)|0.12|
|github|[autamus/registry](https://autamus.io/registry)|0.12|
|github|[spack/spack](https://spack.io)|0.12|
|pypi|[pytest](https://docs.pytest.org/en/latest/)|0.02|
|pypi|[requests](https://pypi.org/project/requests)|0.02|
|pypi|[ruamel.yaml](https://pypi.org/project/ruamel.yaml)|0.02|
|pypi|[jsonschema](https://pypi.org/project/jsonschema)|0.02|
|pypi|[Jinja2](https://pypi.org/project/Jinja2)|0.02|
|pypi|[spython](https://pypi.org/project/spython)|0.02|
|github|[actions/checkout](https://github.com/features/actions)|0.02|
|github|[actions/upload-artifact](https://github.com/actions/upload-artifact)|0.02|
|github|[docker/build-push-action](https://github.com/docker/build-push-action)|0.02|
|github|[docker/login-action](https://github.com/docker/login-action)|0.02|
|github|[docker/setup-buildx-action](https://github.com/docker/setup-buildx-action)|0.02|
|github|[docker/setup-qemu-action](https://github.com/docker/setup-qemu-action)|0.02|
|conda|[libgcc-ng](https://gcc.gnu.org/onlinedocs/gccint/Libgcc.html)|0.02|
|github|[autamus/artifact-dl](https://github.com/autamus/artifact-dl)|0.01|
|github|[autamus/binoc](https://github.com/autamus/binoc)|0.01|
|github|[autamus/buildconfig](https://github.com/autamus/buildconfig)|0.01|
|github|[autamus/builder](https://github.com/autamus/builder)|0.01|
|github|[autamus/librarian](https://github.com/autamus/librarian)|0.01|
|github|[autamus/merge-commits](https://github.com/autamus/merge-commits)|0.01|
|github|[autamus/smuggler](https://github.com/autamus/smuggler)|0.01|
|github|[NextThought/sphinxcontrib-programoutput](https://github.com/NextThought/sphinxcontrib-programoutput)|0.01|
|github|[actions/download-artifact](https://github.com/actions/download-artifact)|0.01|
|github|[actions/setup-python](https://github.com/actions/setup-python)|0.01|
|github|[codecov/codecov-action](https://github.com/codecov/codecov-action)|0.01|
|github|[dorny/paths-filter](https://github.com/dorny/paths-filter)|0.01|
|github|[readthedocs/sphinx_rtd_theme](https://github.com/readthedocs/sphinx_rtd_theme)|0.01|
|github|[sphinx-doc/sphinx](https://github.com/sphinx-doc/sphinx)|0.01|
|github|[ztane/python-Levenshtein](https://github.com/ztane/python-Levenshtein)|0.01|
|conda|[openssl](https://www.openssl.org/)|0.01|
|conda|[libuuid](http://sourceforge.net/projects/libuuid/)|0.01|
|conda|[libstdcxx-ng](https://gcc.gnu.org/)|0.01|
|conda|[libseccomp](https://github.com/seccomp/libseccomp)|0.01|
|conda|[libarchive](http://www.libarchive.org/)|0.01|
|conda|[cni-plugins](https://github.com/containernetworking/plugins)|0.01|


> Note that credit values are rounded and expanded (so shared dependencies are represented as one record) and may not add to 1.0. Rounded values that hit zero are removed.

<!--citelang end-->

