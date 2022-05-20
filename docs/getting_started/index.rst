.. _getting-started:

===============
Getting Started
===============

CiteLang is software for digging into software credit. It provides methods and graph-based modeling to study 
single projects or entire software ecosystems. You can use CiteLang for your research, or a provided tool to generate
software graph artifacts, including (but not limited to):

1. Generate basic software credit trees
2. Give credit accounting for dependencies
3. Choose the filter or threshold you want for credit

Background
==========

We don't believe that "the traditional academic way" of citing papers makes sense for software.
Why should we be trying to generate separate DOIs (digital object identifiers) when we already have
established ways to "publish" and distribute software using package managers? The getting started
guides here will show you the basics of using CiteLang, and of course if you have a question
or issue, please `let us know <https://github.com/vsoch/citelang/issues>`_

Summary of Tools
================

Along with the underlying Python methods to derive your own credit graphs (see `this writeup about the RSEPedia Software Ecosystem <https://vsoch.github.io/2022/rsepedia/>`_) it provides a set of "ready to go" tools that can be used to visualize or understand your project:

 - **Badge** can show an entire credit tree for a project, and are generated as static png or interactive web page.
 - **Credit** can visually show dependency graphs in the terminal.
 - **Graph** can output these same graphs in output formats for graphing software.
 - **Contrib** (contributions) can be assessed on the level of the line. See `this write-up on citelang contrib <https://vsoch.github.io/2022/citelang-contrib/#citelang-contrib>`_ for more detail.
 - **Render** takes a markdown formatting with CiteLang references, and renders into it a summary table. A comparison can be made to .all-contributors.rc, except instead of contributors, we summarize dependencies.
 - **Generate** does the same, but doesn't require a pre-written paper. You can dump out markdown to describe software of your choosing.


.. toctree::
   :maxdepth: 3

   installation
   user-guide
   settings
