import sys
import os
from datetime import datetime
import argparse
import tempfile
import shutil
import json
import subprocess
import glob

from util import load_json
import problem_model as prob
import verdicts
from color_util import cprint, colors
import bash_completion as bc
from verbose import VerbosePrinter
from json_extract import navigate_json
import tests_util as tu


def make_clean_name(name):
    return name.replace(' ', '_').lower()



BASE_DIR = os.environ.get('BASE_DIR')
TESTS_DIR = os.environ.get('TESTS_DIR')


warnings = []

def warn(message):
    warnings.append(message)
    cprint(colors.WARN, message)


vp = VerbosePrinter()


class ExportFailureException(Exception):
    pass


def check_dir_exists(dir_name, title):
    if not os.path.exists(dir_name):
        raise ExportFailureException("{} not found: '{}'.".format(title, dir_name))
    if not os.path.isdir(dir_name):
        raise ExportFailureException("{} not a valid directory: '{}'.".format(title, dir_name))


def wrapped_run(func_name, func):
    def f(*args, **kwargs):
        try:
            return vp.run(func_name, func, *args, **kwargs)
        except (OSError, IOError):
            raise ExportFailureException("Error in calling {}".format(vp.func_repr(func_name, *args, **kwargs)))
    return f

mkdir = wrapped_run("mkdir", os.mkdir)
makedirs = wrapped_run("makedirs", os.makedirs)
copyfile = wrapped_run("copyfile", shutil.copyfile)
move = wrapped_run("move", shutil.move)
make_archive = wrapped_run("make_archive", shutil.make_archive)


class JSONExporter:

    def __init__(self, temp_prob_dir, protocol_version):
        self.temp_prob_dir = temp_prob_dir
        self.protocol_version = protocol_version

    def set_statement_pdf(self, statement_pdf):
        self.statement_pdf = statement_pdf

    def get_absolute_path(self, path):
        return os.path.join(self.temp_prob_dir, path)

    def create_directory(self, path):
        absolute_path = self.get_absolute_path(path)
        makedirs(absolute_path, exist_ok=True)

    def write_to_file(self, path, content):
        absolute_path = self.get_absolute_path(path)
        if isinstance(content, str):
            file_ = open(absolute_path, "w")
        else:
            file_ = open(absolute_path, "wb")
        file_.write(content)
        file_.close()

    def copy_file(self, file, relative_dest):
        absolute_dest = self.get_absolute_path(relative_dest)
        copyfile(file, absolute_dest)


    GRADER_DIR_NAME = "graders"
    MANAGER_DIR_NAME = GRADER_DIR_NAME
    CHECKER_DIR_NAME = "checker"
    TESTS_DIR_NAME = "tests"
    SUBTASKS_DIR_NAME = "subtasks"
    SOLUTION_DIR_NAME = "solutions"
    STATEMENT_DIR_NAME = "statements"


    def _get_task_type_parameters(self, task_type):
        if self.protocol_version == 1:
            task_type_params = prob.general_property("type_params", {})

            if task_type == prob.TASK_TYPE__COMMUNICATION:
                task_type_params["task_type_parameters_Communication_num_processes"] = prob.num_sol_processes()

            if task_type == prob.TASK_TYPE__BATCH:
                if prob.has_grader():
                    compilation_type = "grader"
                else:
                    compilation_type = "alone"
                task_type_params["task_type_parameters_Batch_compilation"] = compilation_type

            return json.dumps(task_type_params)

        # self.protocol_version > 1

        if prob.is_given("task_type_parameters"):
            # Task type parameters list is manually set in PROBLEM_JSON.
            return prob.general_property("task_type_parameters")

        evaluation_type = "comparator" if prob.has_checker() else "diff"

        if task_type == prob.TASK_TYPE__BATCH:
            compilation = "grader" if prob.has_grader() else "alone"
            input_filename = ""
            output_filename = ""
            return [
                compilation,
                [input_filename, output_filename,],
                evaluation_type,
            ]

        if task_type == prob.TASK_TYPE__COMMUNICATION:
            compilation = "stub" if prob.has_grader() else "alone"
            user_io = prob.user_communication_policy()
            return [
                prob.num_sol_processes(),
                compilation,
                user_io,
            ]

        if task_type == prob.TASK_TYPE__TWO_STEPS or task_type == prob.TASK_TYPE__OUTPUT_ONLY:
            return [evaluation_type]

        return []


    def export_problem_global_data(self):
        json_file = "problem.json"
        vp.print("Writing '{}'...".format(json_file))

        task_type = prob.task_type()
        vp.print_var("task_type", task_type)

        problem_data_dict = {
            "protocol_version": self.protocol_version,
            "code": prob.short_name(),
            "name": prob.title(),
            "time_limit": prob.time_limit(),
            "memory_limit": prob.memory_limit()*1024*1024,
            "score_precision": max(0, prob.score_precision()-2),
            "task_type": task_type,
            "task_type_params": self._get_task_type_parameters(task_type),
        }

        if prob.is_given("score_mode"):
            problem_data_dict["score_mode"] = prob.general_property("score_mode")
            
        if prob.is_given("feedback_level"):
            problem_data_dict["feedback_level"] = prob.general_property("feedback_level")

        problem_data_str = json.dumps(problem_data_dict)
        vp.print_var(json_file, problem_data_str)
        self.write_to_file(json_file, problem_data_str)

    def export_statement(self):
        if not self.statement_pdf:
            vp.print("Statement is not exported.")
            return
        vp.print("Exporting statement pdf from '{}'...".format(self.statement_pdf))
        if not os.path.isfile(self.statement_pdf):
            raise ExportFailureException("Statement pdf file not found in the given path '{}'.".format(self.statement_pdf))
        self.create_directory(self.STATEMENT_DIR_NAME)
        self.copy_file(
            self.statement_pdf,
            os.path.join(self.STATEMENT_DIR_NAME, os.path.basename(self.statement_pdf))
        )

    def export_graders(self):
        if not prob.has_grader():
            vp.print("No graders to export.")
            return
        vp.print("Exporting graders...")
        GRADER_DIR = os.environ.get('GRADER_DIR')
        check_dir_exists(GRADER_DIR, "graders directory")
        self.create_directory(self.GRADER_DIR_NAME)
        grader_files = []
        if prob.cpp_enabled():
            grader_files += [
                "cpp/{}.cpp".format(prob.grader_name()),
                "cpp/{}.h".format(prob.short_name()),
            ]
        if prob.java_enabled():
            grader_files += [
                "java/{}.java".format(prob.grader_name()),
            ]
        if prob.python_enabled():
            grader_files += [
                "py/{}.py".format(prob.grader_name()),
            ]
        if prob.pascal_enabled():
            grader_files += [
                "pas/{}.pas".format(prob.grader_name()),
                "pas/{}lib.pas".format(prob.grader_name()),
            ]
        for grader_file in grader_files:
            grader_file_path = os.path.join(GRADER_DIR, grader_file)
            if os.path.isfile(grader_file_path):
                self.copy_file(
                    grader_file_path,
                    os.path.join(self.GRADER_DIR_NAME, os.path.basename(grader_file))
                )
            else:
                vp.print("Grader file '{}' does not exist.".format(grader_file))

    def export_manager(self):
        if not prob.has_manager():
            vp.print("No manager to export.")
            return
        vp.print("Exporting manager...")
        MANAGER_DIR = os.environ.get('MANAGER_DIR')
        check_dir_exists(MANAGER_DIR, "Manager directory")
        manager_files = []
        for p in ["*.cpp", "*.h"]:
            manager_files += glob.glob(os.path.join(MANAGER_DIR, p))
        self.create_directory(self.MANAGER_DIR_NAME)
        for f in manager_files:
            self.copy_file(f, os.path.join(self.MANAGER_DIR_NAME, os.path.basename(f)))

    def export_checker(self):
        if not prob.has_checker():
            vp.print("No checker to export.")
            return
        vp.print("Exporting checker...")
        CHECKER_DIR = os.environ.get('CHECKER_DIR')
        check_dir_exists(CHECKER_DIR, "Checker directory")
        checker_files = []
        for p in ["*.cpp", "*.h"]:
            checker_files += glob.glob(os.path.join(CHECKER_DIR, p))
        self.create_directory(self.CHECKER_DIR_NAME)
        for f in checker_files:
            self.copy_file(f, os.path.join(self.CHECKER_DIR_NAME, os.path.basename(f)))

    def export_testcases(self):
        vp.print("Copying test data...")
        try:
            test_name_list = tu.get_test_names_from_tests_dir(TESTS_DIR)
        except tu.MalformedTestsException as e:
            raise ExportFailureException(str(e))
        vp.print_var("test_name_list", test_name_list)
        available_tests, missing_tests = tu.divide_tests_by_availability(test_name_list, TESTS_DIR)
        if missing_tests:
            warn("Missing tests: "+(", ".join(missing_tests)))
        vp.print_var("available_tests", available_tests)

        self.create_directory(self.TESTS_DIR_NAME)
        for test_name in available_tests:
            clean_test_name = make_clean_name(test_name)
            self.copy_file(
                os.path.join(TESTS_DIR, "{}.in".format(test_name)),
                os.path.join(self.TESTS_DIR_NAME, "{}.in".format(clean_test_name)),
            )
            self.copy_file(
                os.path.join(TESTS_DIR, "{}.out".format(test_name)),
                os.path.join(self.TESTS_DIR_NAME, "{}.out".format(clean_test_name))
            )

    def export_subtasks(self):
        vp.print("Exporting subtasks...")
        try:
            subtasks_tests = tu.get_subtasks_tests_dict_from_tests_dir(TESTS_DIR)
        except tu.MalformedTestsException as e:
            raise ExportFailureException(str(e))

        self.create_directory(self.SUBTASKS_DIR_NAME)
        SUBTASKS_JSON = os.environ.get('SUBTASKS_JSON')
        subtasks_json_data = load_json(SUBTASKS_JSON)
        subtasks_data = dict(navigate_json(subtasks_json_data, 'subtasks', SUBTASKS_JSON))
        for subtask_name, subtask_data in subtasks_data.items():
            vp.print("Export subtask: {}".format(subtask_name))
            self.write_to_file(
                os.path.join(
                    self.SUBTASKS_DIR_NAME,
                    "{subtask_index:02}-{subtask_name}.json".format(subtask_index=subtask_data['index'], subtask_name=subtask_name)
                ),
                json.dumps(
                    {
                        "score": subtask_data['score'],
                        "testcases": [
                            make_clean_name(t)
                            for t in subtasks_tests[subtask_name]
                        ]
                    }
                )
            )

    def export_solutions(self):
        vp.print("Exporting solutions...")
        self.create_directory(self.SOLUTION_DIR_NAME)
        SOLUTION_DIR = os.environ.get('SOLUTION_DIR')
        check_dir_exists(SOLUTION_DIR, "Solutions directory")
        SOLUTIONS_JSON = os.environ.get('SOLUTIONS_JSON')
        solutions_data = dict(load_json(SOLUTIONS_JSON))
        for solution_name, solution_data in solutions_data.items():
            verdict = solution_data.get("verdict", None)
            verdict_dir = make_clean_name(verdicts.get_unified(verdict)) if verdict else "unknown_verdict"
            dest_sol_dir = os.path.join(self.SOLUTION_DIR_NAME, verdict_dir)
            self.create_directory(dest_sol_dir)
            self.copy_file(
                os.path.join(SOLUTION_DIR, solution_name),
                os.path.join(dest_sol_dir, solution_name)
            )

    def export_public_attachment(self):
        PUBLIC_DIR = os.environ.get('PUBLIC_DIR')
        if os.path.isdir(PUBLIC_DIR):
            vp.print("Exporting public data...")
            SCRIPTS = os.environ.get('SCRIPTS')
            make_public_script = os.path.join(SCRIPTS, 'make-public.sh')
            if not os.path.isfile(make_public_script):
                raise ExportFailureException("The 'make-public' script is not available: '{}'".format(make_public_script))
            vp.print("Running make-public script...")
            try:
                subprocess.run(['bash', make_public_script], check=True, capture_output=(not vp.enabled))
            except subprocess.CalledProcessError as e:
                message = "Error in making public attachment.\n{}\n".format(str(e))
                if not vp.enabled:
                    message += "make-pubic stdout:\n{}\nmake-pubic stderr:\n{}\n".format(e.stdout.decode(), e.stderr.decode())
                raise ExportFailureException(message)
            self.create_directory("attachments")
            move(
                os.path.join(BASE_DIR, "{}.zip".format(prob.short_name())),
                self.get_absolute_path("attachments")
            )
        else:
            warn("No public attachment data!")

    def export(self):
        # We don't export generators or validators. Tests are already generated/validated.
        self.export_problem_global_data()
        self.export_statement()
        self.export_graders()
        self.export_manager()
        self.export_checker()
        self.export_testcases()
        self.export_subtasks()
        self.export_solutions()
        self.export_public_attachment()



def create_export_file_name():
    return "{prob_name}-{export_format}-{date}".format(
        prob_name=prob.short_name(),
        export_format="CMS",
        date=datetime.now().strftime("%y-%m-%d-%H-%M-%S%z")
    )


NO_ARCHIVE_FORMAT = 'none'

def get_archive_formats():
    return [(NO_ARCHIVE_FORMAT, "No archiving; export as a directory")] + shutil.get_archive_formats()

def get_archive_format_names():
    return [f[0] for f in get_archive_formats()]


def export(file_name, archive_format, protocol_version, statement_pdf):
    """
    returns the export file name
    """
    vp.print("Exporting '{}' with archive format '{}'...".format(file_name, archive_format))
    vp.print_var("protocol_version", protocol_version)
    with tempfile.TemporaryDirectory(prefix=file_name) as temp_root:
        vp.print_var("temp_root", temp_root)
        temp_prob_dir_name = prob.short_name()
        temp_prob_dir = os.path.join(temp_root, temp_prob_dir_name)
        mkdir(temp_prob_dir)

        exporter = JSONExporter(temp_prob_dir, protocol_version)
        exporter.set_statement_pdf(statement_pdf)
        exporter.export()

        if archive_format == NO_ARCHIVE_FORMAT:
            final_export_file = move(
                temp_prob_dir,
                os.path.join(BASE_DIR, file_name),
            )
        else:
            archive_full_path = make_archive(
                os.path.join(temp_root, file_name),
                archive_format,
                root_dir=temp_root,
                base_dir=temp_prob_dir_name,
            )
            final_export_file = move(archive_full_path, BASE_DIR)
        vp.print_var("final_export_file", final_export_file)
        return final_export_file


def bash_completion_list(argv):
    current_token_info = bc.extract_current_token_info(argv)
    return bc.simple_argument_completion(
        current_token_info=current_token_info,
        available_options=[
            "--help",
            "--verbose",
            "--statement-pdf=",
            "--output-name=",
            "--archive-format=",
        ],
        enable_file_completion=False,
        option_value_completion_functions={
            ("--statement-pdf"):
                bc.complete_with_files,
            ("-o", "--output-name"):
                bc.empty_completion_function,
            ("-a", "--archive-format"):
                bc.simple_option_value_completion_function(get_archive_format_names),
        },
    )


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--bash-completion':
        sys.argv.pop(1)
        bc.print_all(bash_completion_list(sys.argv))
        sys.exit(0)

    parser = argparse.ArgumentParser(
        prog="tps export CMS",
        description="Exporter for CMS -- Contest Management System for IOI.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        'protocol_version',
        metavar='<protocol-version>',
        type=int,
        choices=[1, 2],
        help="""\
The protocol version of the exported package
Currently available versions:
1  The traditionally-used protocol (used up to 2022).
2  Supports more flexible setting of task type parameters (defined in 2022).
Make sure the target CMS server supports the specified protocol version.
"""
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Prints verbose details on values, decisions, and commands being executed.",
    )
    parser.add_argument(
        "--statement-pdf",
        metavar="<statement-pdf-file-path>",
        help="Adds the statement pdf file from the given path.",
    )
    parser.add_argument(
        "-o", "--output-name",
        metavar="<export-output-name>",
        help="Creates the export output with the given name.",
    )
    parser.add_argument(
        "-a", "--archive-format",
        metavar="<archive-format>",
        choices=get_archive_format_names(),
        default="zip",
        help="""\
Creates the export archive with the given format.
Available archive formats:
{}
Default archive format is '%(default)s'.
""".format("\n".join(["  {} {}".format(f[0].ljust(10), f[1]) for f in get_archive_formats()])),
    )
    args = parser.parse_args()

    vp.enabled = args.verbose
    file_name = args.output_name if args.output_name else create_export_file_name()

    try:
        export_file = export(
            file_name,
            args.archive_format,
            args.protocol_version,
            statement_pdf=args.statement_pdf
        )
        if warnings:
            cprint(colors.WARN, "Successfully exported to '{}', but with warnings.".format(export_file))
        else:
            cprint(colors.SUCCESS, "Successfully exported to '{}'.".format(export_file))
    except ExportFailureException as e:
        cprint(colors.FAIL, "Exporting failed: {}".format(e))


if __name__ == '__main__':
    main()
