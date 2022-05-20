# CHANGELOG

This is a manually generated log to track changes to the repository for each release.
Each section should include general headers such as **Implemented enhancements**
and **Merged pull requests**. Critical items to know are:

 - renamed commands
 - deprecated / removed commands
 - changed defaults
 - backward incompatible changes (recipe file format? image file format?)
 - migration guidance (how to convert images?)
 - changed behaviour (recipe sections work differently)

The versions coincide with releases on pip. Only major versions will be released as tags on GitHub.

## [0.0.x](https://github.com/vsoch/citelang/tree/main) (0.0.x)
 - Default contrib does a deep search, with option to add `--shallow` (0.0.29)
 - Adding basic support for parsing CMakeLists.txt (0.0.28)
 - JoSS paper and sort package names in listing (0.0.27)
 - bug with generating markdown for sites in R (0.0.26)
 - using pip to parse requirements files, falling back to static (0.0.25)
 - bug fixes for package managers, adding cache to indicate skip package (0.0.24)
 - do not count empty lines, and allow for skipping files by name (0.0.23)
 - custom filters file can better group authors (0.0.22)
 - adding support for citelang contrib for parsing git history (0.0.21)
 - support for citelang gen/badge from requirements files (0.0.2)
 - bug fixes for badge generator github (0.0.19)
 - refactor of library structure for global cache and settings (0.0.18)
 - fixing display of child->parent credit in graph (0.0.17)
 - improving layout of citelang graphic (0.0.16)
 - static badge added for software (0.0.15)
 - expanding interactive badge into treemap and sunburst (0.0.14)
 - adding basic citelang gen to create markdown files for repos (and actions) (0.0.13)
 - parsing markdown to generate credit table (0.0.12)
 - support for citelang badge to generate interactive html page (0.0.11)
 - first release, and do rounding based on credit (0.0.1)
 - skeleton release (0.0.0)
