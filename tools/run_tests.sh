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
tools/run_tests.sh - every App Builder for FutureBasic check that runs without a Mac

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
txv=""
if [ -d "$here/../Test_Xib_View" ] || [ -d "$here/../test_xib_view" ]; then
    txv="$here/../Test_Xib_View"; [ -d "$txv" ] || txv="$here/../test_xib_view"
    run "fblint: Test_Xib_View" python3 "$here/tools/fblint.py" --headers "$headers" "$txv"
fi
# the SQL Generator module: the runtime's copy, the example project's and Test_Xib_View's are one
sqlgen_same() {
    for f in DataObject.glbl DataObject_Super.incl DataObject.incl; do
        cmp -s "$here/src/Runtime/$f" "$here/src/SQLGeneratorExample/$f" || { echo "differs: src/SQLGeneratorExample/$f"; return 1; }
        if [ -n "$txv" ]; then cmp -s "$here/src/Runtime/$f" "$txv/$f" || { echo "differs: Test_Xib_View/$f"; return 1; }; fi
    done
    echo "SQL Generator: the copies are identical"
}
run "SQL Generator: one module, identical in the runtime, the example project and Test_Xib_View" sqlgen_same
about_same() {
    for app in SQLGeneratorExample LogicBankExample WebToolkitExample RecordFilesExample; do
        for f in "About Imagery.incl" "About Imagery.txt" imagery_logo.png imagery_logo_white.png; do
            cmp -s "$here/src/Shared/$f" "$here/src/$app/$f" || { echo "differs: src/$app/$f"; return 1; }
        done
    done
    echo "About Imagery: the copies are identical"
}
run "About Imagery: one window, identical in src/Shared and each module's example app" about_same
logicbank_same() {
    for f in "Logic Rules.incl" "Logic Row.incl" "Logic Engine.incl" "Data Model.incl"; do
        cmp -s "$here/src/Runtime/$f" "$here/src/LogicBankExample/$f" || { echo "differs: src/LogicBankExample/$f"; return 1; }
    done
    cmp -s "$here/src/SQLGeneratorExample/Rich Text.incl" "$here/src/LogicBankExample/Rich Text.incl" || { echo "differs: Rich Text.incl"; return 1; }
    cmp -s "$here/src/SQLGeneratorExample/Rich Text.incl" "$here/src/RecordFilesExample/Rich Text.incl" || { echo "differs: src/RecordFilesExample/Rich Text.incl"; return 1; }
    echo "LogicBank for FutureBasic: the copies are identical"
}
run "LogicBank for FutureBasic: the module, identical in the runtime and the example project" logicbank_same
run "web: the FastCGI core (compiled here; behind nginx when it is installed)" python3 "$here/tools/check_fastcgi_core.py"
web_same() {
    for d in "src/WebToolkit/Template" "src/WebToolkitExample"; do
        for f in "Web Server.incl" "Web Session.incl" "Web Widgets.incl" "Web Render.incl" "Web Events.incl" "Web Layout.incl" "Web Binding.incl"; do
            cmp -s "$here/src/WebToolkit/$f" "$here/$d/$f" || { echo "differs: $d/$f"; return 1; }
        done
        for f in web.js web.css; do
            cmp -s "$here/src/WebToolkit/Resources/$f" "$here/$d/$f" || { echo "differs: $d/$f"; return 1; }
        done
        for f in "Server Window.incl" "Web App.glbl" "Web App.main"; do
            cmp -s "$here/src/WebToolkit/Template/$f" "$here/$d/$f" || { echo "differs: $d/$f"; return 1; }
        done
    done
    for f in "Data Model.incl" "Logic Rules.incl" "Logic Row.incl" "Logic Engine.incl"; do
        cmp -s "$here/src/Runtime/$f" "$here/src/WebToolkitExample/$f" || { echo "differs: src/WebToolkitExample/$f"; return 1; }
    done
    for f in "Data Memory.incl" "Rules.incl" "Model.json"; do
        cmp -s "$here/src/LogicBankExample/$f" "$here/src/WebToolkitExample/$f" || { echo "differs: src/WebToolkitExample/$f"; return 1; }
    done
}
run "web: the Web Toolkit, identical in the module, its app template and the Orders example" web_same
run "web: web.js against the toolkit's protocol, in headless Chromium (tools/web_toolkit_reference.py)" python3 "$here/tools/web_toolkit_reference.py" --test
run "web: the layout rules - XIB to web page (tools/web_layout_reference.py)" python3 "$here/tools/web_layout_reference.py" --test
run "web: Web Layout.incl's XIB reader, compiled with GNUstep, against the rules (tools/check_web_layout.py)" python3 "$here/tools/check_web_layout.py"
run "web: the layout tool in headless Chromium - preview, editing, saving (tools/check_layout_tool.py)" python3 "$here/tools/check_layout_tool.py"
run "licences: the reference signs and verifies (valid, tampered, expired, another product, another key)" python3 "$here/tools/licence_reference.py" --test
run "licences: the Mac test program carries Licence.incl's verify part unchanged" python3 "$here/tools/licence_reference.py" --mac-test-check
run "LogicBank example: the story's every value, worked out by the reference engine" python3 "$here/tools/logicbank_example_reference.py"
run "record files: the B-tree index (C, compiled here) - random runs against a sorted list, the file read back by the reference" python3 "$here/tools/check_record_index.py"
run "record files: the example's sample data and its SQLite comparison (compiled here)" python3 "$here/tools/check_record_files_example.py"
run "pill buttons: one module, identical in the Studio and the runtime" cmp "$here/src/AppBuilder/Pill Buttons.incl" "$here/src/Runtime/Pill Buttons.incl"
run "logic engine: scenarios (Python reference)" python3 "$here/tools/logic_reference.py" --test "$db"
run "logic engine: every rule proven (each rule left out must fail a scenario)" python3 "$here/tools/logic_reference.py" --prove "$db"
run "rules bridge: declare_logic.py import / export, Rules.json check, FB generation" python3 "$here/tools/rules_bridge.py" --test "$db"

work=$(mktemp -d)
run "logic engine: the FB test project builds from the runtime and lints clean" sh -c "python3 '$here/tools/make_logic_test.py' '$db' '$work/LogicTest' >/dev/null && python3 '$here/tools/fblint.py' --headers '$headers' '$work/LogicTest'"
rm -rf "$work"
# the API Logic Server contract (Professional): only when a server answers on localhost:5656
if python3 "$here/tools/als_contract.py" http://localhost:5656 >/dev/null 2>&1 || [ $? -ne 2 ]; then
    run "Professional: the API Logic Server contract, against the server on localhost:5656" python3 "$here/tools/als_contract.py" http://localhost:5656
    alsdb="${ALS_DB:-}"
    if [ -n "$alsdb" ] && [ -f "$alsdb" ]; then
        run "Professional: the SQL Generator's two sides give the same rows (SQL on the server's db, JSON:API on the server)" python3 "$here/tools/jsonapi_reference.py" --test "$alsdb" http://localhost:5656
    else
        echo; echo "== Professional: SQL vs JSON:API side by side - skipped (set ALS_DB to the server's database/db.sqlite)"
    fi
else
    echo; echo "== Professional: the API Logic Server contract - skipped (no server on localhost:5656; docs/design/ALS Contract.md)"
fi
# the Open ALS Project screen's logic: GitHub addresses always; folders, files and the Studio model
# on the ALS projects in ALS_PROJECTS; public repositories over raw.githubusercontent.com with ALS_GITHUB=1
run "Professional: the page designer - Pages.json, the links proposed on a drop, a page resolved (Northwind fixture, the samples)" python3 "$here/tools/pages_reference.py" --test
run "ALS project: addresses, folders and files, the Studio model with its lookups" python3 "$here/tools/als_project_reference.py" --test ${ALS_PROJECTS:-} ${ALS_GITHUB:+--github}
# the ALS model reader (Professional): database/models.py read as text, compared with SQLAlchemy's view
# ALS_PROJECTS: ALS project folders (space-separated); ALS_PYTHON: the Python of the ALS install
if [ -n "${ALS_PROJECTS:-}" ] && [ -x "${ALS_PYTHON:-}" ]; then
    for project in $ALS_PROJECTS; do
        run "Professional: models.py read as text = SQLAlchemy's model ($(basename "$project"))" python3 "$here/tools/models_py_reference.py" "$project" "$ALS_PYTHON"
    done
else
    echo; echo "== Professional: models.py reader vs SQLAlchemy - skipped (set ALS_PROJECTS and ALS_PYTHON)"
fi
# the sample applications (samples/*): each one's rules scenario by scenario (with the purge of its sample
# data), every rule proven, and its FB Rules.incl linted with the runtime
sample_lint() {
    t=$(mktemp -d)
    for f in "Data SQLite.incl" DataObject.glbl DataObject_Super.incl DataObject.incl "Data Model.incl" "Data Records.incl" "Logic Rules.incl" "Logic Row.incl" "Logic Engine.incl"; do cp "$here/src/Runtime/$f" "$t/"; done
    cp "$here/samples/$1/Rules.incl" "$t/"
    python3 "$here/tools/fblint.py" --headers "$headers" "$t"; r=$?; rm -rf "$t"; return $r
}
for sample in Telecom Customs FlightPlanner; do
    run "$sample sample: its scenarios through the rules, and the purge of its sample data" python3 "$here/samples/$sample/test_rules.py"
    run "$sample sample: every rule proven (each left out must fail a scenario)" python3 "$here/samples/$sample/test_rules.py" --prove
    run "$sample sample: Rules.incl lints with the runtime" sample_lint "$sample"
done
run "generated pages: App Pages.incl, as AppPagesSource writes it, lints with the runtime and templates" python3 "$here/tools/check_app_pages.py" "$docs"
run "model diagram: the ERD page draws the model and rules, opens / closes, drags, selects" python3 "$here/tools/check_erd_page.py" "$db"

echo
if [ $status -eq 0 ]; then echo "run_tests: all passed"; else echo "run_tests: FAILURES above"; fi
exit $status
