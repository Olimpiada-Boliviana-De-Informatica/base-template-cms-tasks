#!/bin/bash

set -euo pipefail

source "${INTERNALS}/util.sh"
source "${INTERNALS}/problem_util.sh"

# TODO: make this design cleaner
problem_code="$(get_problem_data 'code')"
tps_web_url="$(get_problem_data 'web_url')"

commit=$(git log --pretty=format:'%H' -n 1)

analysis_url="${tps_web_url}/problem/${problem_code}/${commit}/analysis"

echo "Openning address: '${analysis_url}'"

function try_open {
	if which "$1" &> "/dev/null"; then
		"$@"
		exit
	fi
}

try_open "xdg-open" "${analysis_url}"
try_open "gnome-open" "${analysis_url}"
try_open "open" "${analysis_url}"
try_open "start" "${analysis_url}"
try_open "cygstart" "${analysis_url}"
try_open ""${PYTHON}"" "-mwebbrowser" "${analysis_url}"

error_exit 1 "Could not open the browser"
