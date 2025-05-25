#!/bin/bash

set -euo pipefail


FORMATTING_CONFIG_FILE="${FORMATTING_SCRIPTS_DIR}/internal/clang-format.config"


function errcho {
	>&2 echo "$@"
}

function error_exit {
	local -r exit_code=$1; shift
	errcho "$@"
	exit ${exit_code}
}


function command_exists {
	local -r cmd_name="$1"; shift
	command -v "${cmd_name}" &> "/dev/null"
}

function check_clang_format_cmd {
	command_exists "clang-format" ||
		error_exit 4 "\
Command clang-format not found.
Install it with running:
    sudo apt install clang-format
The version of clang-format must be >= 14
"
}


function list_files_to_format {
	{
		ls -1 "${task_dir}/grader/cpp/"*.h
		if [ ! -e "${task_dir}/grader/manager.cpp" ]; then
			ls -1 "${task_dir}/grader/cpp/grader.cpp"
		fi
		ls -1 "${task_dir}/public/cpp/"*.h
		ls -1 "${task_dir}/public/cpp/"*.cpp
	} 2> "/dev/null" || true
}

function set_files_to_format {
	local -r task_dir="$1"; shift

	local files_to_format_str
	files_to_format_str="$(list_files_to_format)"
	readonly files_to_format_str

	[ -n "${files_to_format_str}" ] ||
		error_exit 2 "No files to format"

	files_to_format=()
	local line
	while IFS= read -r line; do
		files_to_format+=("${line}")
	done <<< "${files_to_format_str}"
}


function verify_format {
	local -r file_to_format="$1"; shift
	clang-format "--style=file:${FORMATTING_CONFIG_FILE}" --dry-run --Werror "${file_to_format}" 2>&1
}

function run_script__verify_format {
	local -r task_dir="$1"; shift

	check_clang_format_cmd

	local files_to_format
	set_files_to_format "${task_dir}"

	local have_errors="false"
	local file_to_format
	for file_to_format in "${files_to_format[@]}"; do
		echo "Verify format of '${file_to_format}'..."
		if verify_format "${file_to_format}"; then
			echo OK
		else
			have_errors="true"
		fi
		echo "================================================================================"
	done
	if "${have_errors}"; then
		return 3
	fi
}



function apply_format {
	local -r file_to_format="$1"; shift
	clang-format "--style=file:${FORMATTING_CONFIG_FILE}" -i "${file_to_format}"
}

function run_script__apply_format {
	local -r task_dir="$1"; shift

	check_clang_format_cmd

	local files_to_format
	set_files_to_format "${task_dir}"

	local file_to_format
	for file_to_format in "${files_to_format[@]}"; do
		echo "Applying format on '${file_to_format}'..."
		apply_format "${file_to_format}"
		echo
	done
}
