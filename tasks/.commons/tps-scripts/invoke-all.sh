#!/bin/bash

set -euo pipefail

source "${INTERNALS}/util.sh"
source "${INTERNALS}/problem_util.sh"
source "${INTERNALS}/invoke_util.sh"

function usage {
	errcho "Usage: <invoke-all> [options]"
	errcho "Options:"

	errcho -e "  -h, --help"
	errcho -e "\tShows this help."

	errcho -e "  -s, --sensitive"
	errcho -e "\tTerminates on the first error and shows the error details."

	errcho -e "  -w, --warning-sensitive"
	errcho -e "\tTerminates on the first warning or error and shows the details."

    errcho -e "  -v, --verbose"
	errcho -e "\tShows run results for each invoked test."

	errcho -e "  --solution=<solution-name-pattern>"
	errcho -e "\tInvokes only solutions matching the given pattern. Examples: solution, 'solution-*', '*-wa'"

	errcho -e "  -t, --test=<test-name-pattern>"
	errcho -e "\tInvokes only tests matching the given pattern. Examples: 1-01, '1-*', '1-0?'"
	errcho -e "\tMultiple patterns can be given using commas or pipes. Examples: '1-01, 2-*', '?-01|*2|0-*'"
	errcho -e "\tNote: Use quotation marks or escaping (with '\\') when using wildcards in the pattern to prevent shell expansion."
	errcho -e "\t      Also, use escaping (with '\\') when separating multiple patterns using pipes."

	errcho -e "      --tests-dir=<tests-directory-path>"
	errcho -e "\tOverrides the location of the tests directory"

	errcho -e "      --no-tle"
	errcho -e "\tRemoves the default time limit on the execution of the solution."
	errcho -e "\tActually, a limit of 24 hours is applied."

	errcho -e "      --time-limit=<time-limit>"
	errcho -e "\tOverrides the (soft) time limit on the solution execution."
	errcho -e "\tGiven in seconds, e.g. --time-limit=1.2 means 1.2 seconds"

	errcho -e "      --hard-time-limit=<hard-time-limit>"
	errcho -e "\tSolution process will be killed after <hard-time-limit> seconds."
	errcho -e "\tDefaults to <time-limit> + 2."
	errcho -e "\tNote: The hard time limit must be greater than the (soft) time limit."
}


tests_dir="${TESTS_DIR}"
solution_dir="${SOLUTION_DIR}$"
SHOW_REASON="false"
SENSITIVE_RUN="false"
WARNING_SENSITIVE_RUN="false"
SPECIFIED_SOLUTIONS_PATTERN="*"
SPECIFIC_TESTS="false"
SPECIFIED_TESTS_PATTERN=""
SKIP_CHECK="false"
VERBOSE_INVOKE="false"


function handle_option {
	local -r curr_arg="$1"; shift
	case "${curr_arg}" in
		-h|--help)
			usage
			exit 0
			;;
		-s|--sensitive)
			SENSITIVE_RUN="true"
			;;
		-w|--warning-sensitive)
			SENSITIVE_RUN="true"
			WARNING_SENSITIVE_RUN="true"
			;;
        -v|--verbose)
			VERBOSE_INVOKE="true"
			;;
		--solution=*)
			fetch_arg_value "SPECIFIED_SOLUTIONS_PATTERN" "-@" "--solution" "solution name"
			;;
		-t|--test=*)
			fetch_arg_value "SPECIFIED_TESTS_PATTERN" "-t" "--test" "test name"
			SPECIFIC_TESTS="true"
			;;
		--tests-dir=*)
			fetch_arg_value "tests_dir" "-@" "--tests-dir" "tests directory path"
			;;
		--no-tle)
			SOFT_TL=$((24*60*60))
			;;
		--time-limit=*)
			fetch_arg_value "SOFT_TL" "-@" "--time-limit" "soft time limit"
			;;
		--hard-time-limit=*)
			fetch_arg_value "HARD_TL" "-@" "--hard-time-limit" "hard time limit"
			;;
		*)
			invalid_arg_with_usage "${curr_arg}" "undefined option"
			;;
	esac
}

function handle_positional_arg {
	local -r curr_arg="$1"; shift
	invalid_arg_with_usage "${curr_arg}" "meaningless argument"
}

argument_parser "handle_positional_arg" "handle_option" "invalid_arg_with_usage" "$@"

check_invoke_prerequisites

check_and_init_limit_variables

sensitive check_directory_exists "Tests directory" "${tests_dir}"

export SHOW_REASON SENSITIVE_RUN WARNING_SENSITIVE_RUN SPECIFIC_TESTS SPECIFIED_TESTS_PATTERN SKIP_CHECK SOFT_TL HARD_TL VERBOSE_INVOKE


recreate_dir "${LOGS_DIR}"

export STATUS_PAD=20

compile_checker_if_needed

ret=0
for solution in "${SOLUTION_DIR}"/$SPECIFIED_SOLUTIONS_PATTERN; do
    sensitive check_file_exists "Solution file" "${solution}"

    echo
    echo "${solution}"
    echo

	recreate_dir "${LOGS_DIR}"

    compile_solution_if_needed "false" "solution.compile" "solution" "${solution}"

    cret=0
    "${PYTHON}" "${INTERNALS}/invoke.py" "${tests_dir}" "${solution}" || cret=$?

    if [ ${cret} -eq 0 ]; then
	    cecho success "Success."
    else
	    cecho fail "Fail."
        ret=1
    fi
done


echo

if [ ${ret} -eq 0 ]; then
	cecho success "Finished."
else
	cecho fail "Finished."
fi

exit ${ret}
