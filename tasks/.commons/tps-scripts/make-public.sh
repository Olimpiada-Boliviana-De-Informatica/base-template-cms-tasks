#!/bin/bash

set -euo pipefail

source "${INTERNALS}/util.sh"
source "${INTERNALS}/problem_util.sh"



function usage {
	errcho -ne "\
Usage:
  tps make-public [options]

Description:
  Creates/updates the public directory
   and creates the public attachment package as an archive file.

Options:
\
  -h, --help
        Shows this help.
\
  --no-git-changes
        Checks if there are any git changes in the public directory
         after the execution of this command.
        If there are any changes, the command terminates with a non-zero exit code
         without creating the attachment archive file.
        This feature is mainly used by the automatic checking scripts to make sure
         that no further changes are introduced by running this command.
"
}


CHECK_GIT_CHANGES="false"

function handle_option {
	local -r curr_arg="$1"; shift
	case "${curr_arg}" in
		-h|--help)
			usage_exit 0
			;;
		--no-git-changes)
			CHECK_GIT_CHANGES="true"
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



grader="${GRADER_DIR}"
public="${PUBLIC_DIR}"

problem_name="$(get_problem_data 'short_name')"
public_grader_name="$(get_problem_data 'public_grader_name')"

attachment_name="${problem_name}.zip"
public_files="${PUBLIC_DIR}/files"

function fix() {
	cecho yellow -n "fix: "
	echo "$@"
	check_file_exists "file" "${public}/$1"
	dos2unix -q "${public}/$1" > "/dev/null"
}

function pgg() {
	cecho yellow -n "pgg: "
	echo "$@"
	local -r input_grader="${grader}/$1"
	local -r output_grader="${public}/$1"
	check_file_exists "file" "${input_grader}"
	"${PYTHON}" "${INTERNALS}/pgg.py" "${input_grader}" "${output_grader}"
	fix "$@"
}

function make_grader() {
	pgg "$@"
}

function make_public() {
	fix "$@"
}

extention_point="${TEMPLATES}/make_public_extension.sh"

if [ -f "${extention_point}" ]; then
	source "${extention_point}"
fi

function replace_tokens {
	sed -e "s/PROBLEM_NAME_PLACE_HOLDER/${problem_name}/g" \
	    -e "s/GRADER_NAME_PLACE_HOLDER/${public_grader_name}/g"
}

sensitive check_file_exists "Public package description file" "${public_files}"


if "${CHECK_GIT_CHANGES}"; then
	command_exists "git" ||
		error_exit 4 "Command 'git' is not available."
fi


pushdq "${PUBLIC_DIR}"

while read raw_line; do
	line=$(echo ${raw_line} | replace_tokens | xargs)
	if [ -z "${line}" -o "${line:0:1}" == "#" ]; then
		continue
	fi

	args=($line)

	if [ "${args[0]}" == "copy_test_inputs" ]; then
		gen_data_file="${BASE_DIR}/${args[1]}"
		relative_public_tests_dir="${args[2]}"
		relative_generated_tests_dir="${args[3]}"
		generated_tests_dir="${BASE_DIR}/${relative_generated_tests_dir}"
		sensitive check_file_exists "Generation data file" "${gen_data_file}"
		#function is needed as "sensitive" does not work with multiple lines
		function check_tests_exist {
			"${PYTHON}" "${INTERNALS}/list_tests.py" "${gen_data_file}" | while read test_name; do
				generated_input="${generated_tests_dir}/${test_name}.in"
				sensitive check_file_exists "input file" "${generated_input}"
			done
		}
		sensitive check_tests_exist
		cecho yellow "Copying inputs in '${relative_generated_tests_dir}' to '$(basename ${public})/${relative_public_tests_dir}'; assuming data to be up to date."
		absolute_public_tests_dir="${PUBLIC_DIR}/${relative_public_tests_dir}"
		recreate_dir "${absolute_public_tests_dir}"
		"${PYTHON}" "${INTERNALS}/list_tests.py" "${gen_data_file}" | while read test_name; do
			generated_input="${generated_tests_dir}/${test_name}.in"
			relative_public_input="${relative_public_tests_dir}/${test_name}.in"
			absolute_public_input="${PUBLIC_DIR}/${relative_public_input}"
			cecho yellow -n "copy: "
			echo "${relative_public_input}"
			cp "${generated_input}" "${absolute_public_input}"
			dos2unix -q "${absolute_public_input}" > "/dev/null"
		done
		continue
	fi

	if [ "${args[0]}" == "run" ]; then
		[ ${#args[@]} -ge 2 ] ||
			error_exit 3 "Error: empty run command."
		l="${line#"run"}"
		cecho yellow -n "run: "
		echo "${l}"
		ret=0
		eval "${l}" || ret=$?
		[ ${ret} -eq 0 ] ||
			error_exit "${ret}" "Run exited with code ${ret}."
		continue
	fi

	file="${args[1]}"
	make_${line}
	if grep -iq secret "${file}"; then
#		error_exit 1 "Secret found in '${file}'"
    echo "Secret found in '${file}'"
	fi
	if [ "${file: -3}" == ".sh" ]; then
		chmod +x "${file}"
	fi
done < "${public_files}"


if "${CHECK_GIT_CHANGES}"; then
	cecho yellow "Running git status..."
	git status -- "."
	git_stat="$(git status --porcelain -- ".")"
	if [ -z "${git_stat}" ]; then
		cecho yellow "No git changes found in the public directory."
	else
		cecho error -n "Error: "
		echo "Found git changes in the public directory."
		exit 3
	fi
fi


cecho yellow "Creating the attachment package..."

rm -f "${attachment_name}"

while read raw_line; do
	line=$(echo ${raw_line} | replace_tokens | xargs)
	if [ -z "${line}" -o "${line:0:1}" == "#" ]; then
		continue
	fi

	args=($line)

	if [ "${args[0]}" == "copy_test_inputs" ]; then
		gen_data_file="${BASE_DIR}/${args[1]}"
		relative_public_tests_dir="${args[2]}"
		"${PYTHON}" "${INTERNALS}/list_tests.py" "${gen_data_file}" | while read test_name; do
			relative_public_input="${relative_public_tests_dir}/${test_name}.in"
			echo "${relative_public_input}"
		done
		continue
	fi

	if [ "${args[0]}" == "run" ]; then
		continue
	fi

	file="${args[1]}"
	echo "${file}"
done < "${public_files}" | zip -@ "${attachment_name}"

popdq

mv "${PUBLIC_DIR}/${attachment_name}" "${BASE_DIR}/"

cecho yellow "Created attachment '${attachment_name}'."

cecho success OK
