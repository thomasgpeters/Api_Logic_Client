#!/bin/sh
# Every check that runs without a Mac, in one go - see docs/TESTING.md.
#
#     tools/run_tests.sh [path to FutureBasic_Documentation]
#
# Default: the FutureBasic_Documentation clone beside this repository. It provides the
# toolbox headers (for fblint) and the Northwind database (for the logic scenarios); the
# database is only ever copied, never changed.
set -u

usage() {
    cat <<'HELP'
tools/run_tests.sh - every Api Logic Client check that runs without a Mac

Usage:
    tools/run_tests.sh [path to FutureBasic_Documentation]
    tools/run_tests.sh --help

Runs, in order:
    1. fblint on src/ (and on Test_Xib_View when it is cloned beside this repository)
    2. the logic engine's scenarios      (tools/logic_reference.py --test)
    3. every rule proven                 (tools/logic_reference.py --prove)
    4. the rules bridge: declare_logic.py import / export, check, FB generation (tools/rules_bridge.py --test)
    5. the FB test project assembles and lints clean (tools/make_logic_test.py)
    6. the generated App Pages.incl lints with the runtime and templates (tools/check_app_pages.py)
    7. the model diagram page: filled as ERD Generator.incl fills it, drawn in headless Chromium
       when node + Playwright are installed (tools/check_erd_page.py)

The FutureBasic_Documentation clone (default: beside this repository) provides the toolbox
headers and the Northwind database; the database is only ever copied, never changed.
Exit status: 0 when everything passed, 1 when something failed, 2 when the clone is missing.
More, including the checks on a Mac: docs/TESTING.md
HELP
}

case "${1:-}" in
    -h|--help|help) usage; exit 0 ;;
esac

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
    echo "FutureBasic_Documentation not found (looked in $docs) - pass its path as the first argument (see --help)."
    exit 2
fi

run "fblint: the generator and runtime" python3 "$here/tools/fblint.py" --headers "$headers" "$here/src"
if [ -d "$here/../Test_Xib_View" ] || [ -d "$here/../test_xib_view" ]; then
    txv="$here/../Test_Xib_View"; [ -d "$txv" ] || txv="$here/../test_xib_view"
    run "fblint: Test_Xib_View" python3 "$here/tools/fblint.py" --headers "$headers" "$txv"
fi
run "logic engine: scenarios (Python reference)" python3 "$here/tools/logic_reference.py" --test "$db"
run "logic engine: every rule proven (each rule left out must fail a scenario)" python3 "$here/tools/logic_reference.py" --prove "$db"
run "rules bridge: declare_logic.py import / export, Rules.json check, FB generation" python3 "$here/tools/rules_bridge.py" --test "$db"

work=$(mktemp -d)
run "logic engine: the FB test project builds from the runtime and lints clean" sh -c "python3 '$here/tools/make_logic_test.py' '$db' '$work/LogicTest' >/dev/null && python3 '$here/tools/fblint.py' --headers '$headers' '$work/LogicTest'"
rm -rf "$work"
run "generated pages: App Pages.incl, as AppPagesSource writes it, lints with the runtime and templates" python3 "$here/tools/check_app_pages.py" "$docs"
run "model diagram: the ERD page draws the model and rules, opens / closes, drags, selects" python3 "$here/tools/check_erd_page.py" "$db"

echo
if [ $status -eq 0 ]; then echo "run_tests: all passed"; else echo "run_tests: FAILURES above"; fi
exit $status
