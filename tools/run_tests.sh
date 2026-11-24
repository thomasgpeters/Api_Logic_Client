#!/bin/sh
# Every check that runs without a Mac, in one go - see docs/TESTING.md.
#
#     tools/run_tests.sh [path to FutureBasic_Documentation]
#
# Default: the FutureBasic_Documentation clone beside this repository. It provides the
# toolbox headers (for fblint) and the Northwind database (for the logic scenarios); the
# database is only ever copied, never changed.
set -u
here=$(cd "$(dirname "$0")/.." && pwd)
docs=${1:-"$here/../FutureBasic_Documentation"}
[ -d "$docs" ] || docs="$here/../futurebasic_documentation"
headers="$docs/Toolboxes/Headers"
db="$docs/nw/database/db.sqlite"
status=0

run() {
    echo
    echo "== $1"
    shift
    "$@" || status=1
}

if [ ! -d "$headers" ] || [ ! -f "$db" ]; then
    echo "FutureBasic_Documentation not found (looked in $docs) - pass its path as the first argument."
    exit 2
fi

run "fblint: the generator and runtime" python3 "$here/tools/fblint.py" --headers "$headers" "$here/src"
if [ -d "$here/../Test_Xib_View" ] || [ -d "$here/../test_xib_view" ]; then
    txv="$here/../Test_Xib_View"; [ -d "$txv" ] || txv="$here/../test_xib_view"
    run "fblint: Test_Xib_View" python3 "$here/tools/fblint.py" --headers "$headers" "$txv"
fi
run "logic engine: scenarios (Python reference)" python3 "$here/tools/logic_reference.py" --test "$db"
run "logic engine: every rule proven (each rule left out must fail a scenario)" python3 "$here/tools/logic_reference.py" --prove "$db"

work=$(mktemp -d)
run "logic engine: the FB test project builds from the runtime and lints clean" sh -c "python3 '$here/tools/make_logic_test.py' '$db' '$work/LogicTest' >/dev/null && python3 '$here/tools/fblint.py' --headers '$headers' '$work/LogicTest'"
rm -rf "$work"

echo
if [ $status -eq 0 ]; then echo "run_tests: all passed"; else echo "run_tests: FAILURES above"; fi
exit $status
