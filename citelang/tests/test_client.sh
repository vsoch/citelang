#!/bin/bash

echo
echo "************** START: test_client.sh **********************"

# Create temporary testing directory
echo "Creating temporary directory to work in."
here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
root="$( dirname "${here}" )"

. $here/helpers.sh

# Create temporary testing directory
tmpdir=$(mktemp -d)
output=$(mktemp ${tmpdir:-/tmp}/citelang_test.XXXXXX)
printf "Created temporary directory to work in. ${tmpdir}\n"

# Make sure it's installed
if ! command -v citelang &> /dev/null
then
    printf "citelang is not installed\n"
    exit 1
else
    printf "citelang is installed\n"
fi

# Create a temporary config file, module folder, etc.
settings=$tmpdir/settings.yml
export CITELANG_SETTINGS_FILE=$settings
cache=$tmpdir/cache
mkdir -p $cache
cp $root/settings.yml $settings

echo
echo "#### Testing base client "
runTest 0 $output citelang --version

echo
echo "#### Testing config "
runTest 0 $output citelang config --help
runTest 0 $output citelang config set "cache_dir:$cache"
runTest 0 $output citelang config get "cache_dir"

echo
echo "#### Testing list "
runTest 0 $output citelang list --help
runTest 0 $output citelang list

echo
echo "#### Testing package "
runTest 0 $output citelang package --help
runTest 0 $output citelang package pypi requests
runTest 0 $output citelang package pypi requests --json
runTest 0 $output citelang package pypi requests --outfile $tmpdir/requests.json

echo
echo "#### Testing deps "
runTest 0 $output citelang deps --help
runTest 0 $output citelang deps pypi requests
runTest 0 $output citelang deps pypi requests --json
runTest 0 $output citelang deps pypi requests --outfile $tmpdir/requests.json

echo
echo "#### Testing graph "
runTest 0 $output citelang graph --help
runTest 0 $output citelang graph pypi requests
runTest 0 $output citelang graph pypi requests --fmt cypher
runTest 0 $output citelang graph pypi requests --fmt gexf
runTest 0 $output citelang graph pypi requests --fmt dot

echo
echo "#### Testing credit "
runTest 0 $output citelang credit --help
runTest 0 $output citelang credit pypi requests
runTest 0 $output citelang credit pypi requests --fmt cypher
runTest 0 $output citelang credit pypi requests --fmt gexf
runTest 0 $output citelang credit pypi requests --fmt dot

# echo
# echo "#### Testing render "
# runTest 0 $output citelang render ../../examples/paper.md
# runTest 0 $output citelang render ../../examples/paper.md --outfile paper.md
# cat paper.md

# echo
# echo "#### Testing gen "
# runTest 0 $output citelang gen pypi requests

echo
echo "#### Testing badge "
runTest 0 $output citelang badge pypi requests
# runTest 0 $output citelang badge --template sunburst pypi requests
# runTest 0 $output citelang badge --template treemap pypi requests

echo
echo "#### Testing cache "
runTest 0 $output citelang cache --help
runTest 0 $output citelang cache
runTest 0 $output citelang cache --clear --force

rm -rf ${tmpdir}
