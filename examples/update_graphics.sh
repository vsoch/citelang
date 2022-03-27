#!/bin/bash

# Example and helper script to update citelang graphics!
filename=`basename "$0"`
here=`dirname $filename`
root=`dirname $here`

citelang badge pypi citelang --min-credit 0.001 --outfile docs/assets/img/pypi-citelang.png --force
citelang badge pypi requests --outfile docs/getting_started/img/badge-pypi-requests.png --force
citelang badge pypi requests --min-credit 0.001 --outfile docs/getting_started/img/badge-pypi-requests-deeper.png --force
