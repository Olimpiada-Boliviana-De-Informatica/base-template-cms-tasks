
import sys
import os
import json
import re
import subprocess

from util import get_bool_environ
import problem_model as prob
import verdicts
from gen_data_parser import DataVisitor, parse_data_or_throw, DataParseError
from color_util import cprint, colors

BASE_DIR = os.environ.get('BASE_DIR')

WEB_TERMINAL = get_bool_environ('WEB_TERMINAL')

PROBLEM_JSON = os.environ.get('PROBLEM_JSON')
SOLUTIONS_JSON = os.environ.get('SOLUTIONS_JSON')
SUBTASKS_JSON = os.environ.get('SUBTASKS_JSON')
GEN_DATA = os.environ.get('GEN_DATA')
GEN_DIR = os.environ.get('GEN_DIR')
VALIDATOR_DIR = os.environ.get('VALIDATOR_DIR')
SOLUTION_DIR = os.environ.get('SOLUTION_DIR')
CHECKER_DIR = os.environ.get('CHECKER_DIR')
GRADER_DIR = os.environ.get('GRADER_DIR')
MANAGER_DIR = os.environ.get('MANAGER_DIR')
STATEMENT_DIR = os.environ.get('STATEMENT_DIR')


def get_relative(full_path):
    return full_path[len(BASE_DIR)+1:] if full_path.startswith(BASE_DIR) else full_path

GEN_DATA_RELATIVE = get_relative(GEN_DATA)
SUBTASKS_JSON_RELATIVE = get_relative(SUBTASKS_JSON)

git_enabled = prob.verify_git()
git_remote_name = "origin"


necessary_files = [
    os.path.join(VALIDATOR_DIR, 'Makefile'),
    os.path.join(GEN_DIR, 'Makefile'),
    GEN_DATA,
]

semi_necessary_files = [
    os.path.join(VALIDATOR_DIR, 'testlib.h'),
    os.path.join(GEN_DIR, 'testlib.h'),
]

if prob.has_grader():
    if prob.cpp_enabled():
        necessary_files += [
            os.path.join(GRADER_DIR, 'cpp/%s.h' % prob.short_name()),
            os.path.join(GRADER_DIR, 'cpp/%s.cpp' % prob.grader_name()),
        ]
    if prob.java_enabled():
        necessary_files += [
            os.path.join(GRADER_DIR, 'java/%s.java' % prob.grader_name()),
        ]
    if prob.pascal_enabled():
        necessary_files += [
            os.path.join(GRADER_DIR, 'pas/%s.pas' % prob.grader_name()),
        ]
    if prob.python_enabled():
        necessary_files += [
            os.path.join(GRADER_DIR, 'py/%s.py' % prob.grader_name()),
        ]

if prob.has_manager():
    necessary_files += [
        os.path.join(MANAGER_DIR, 'Makefile'),
        os.path.join(MANAGER_DIR, 'manager.cpp'),
    ]

if prob.has_checker():
    necessary_files += [
        os.path.join(CHECKER_DIR, 'Makefile'),
    ]
    semi_necessary_files += [
        os.path.join(CHECKER_DIR, 'checker.cpp'),
        os.path.join(CHECKER_DIR, 'testlib.h'),
    ]


if sys.version_info >= (3,):
    string_types = (str,)
else:
    string_types = (str, eval("unicode")) #pylint: disable=eval-used


class Verification:
    errors = []
    warnings = []
    namespace = ''

    @classmethod
    def error(cls, description):
        cls.errors.append('ERROR: {} - {}'.format(cls.namespace, description))

    @classmethod
    def warning(cls, description):
        cls.warnings.append('WARNING: {} - {}'.format(cls.namespace, description))

    @classmethod
    def report(cls):
        for _error in cls.errors:
            cprint(colors.ERROR, _error)

        if not cls.errors:
            if cls.warnings:
                cprint(colors.WARN, "verified, but with some warnings.")
            else:
                cprint(colors.OK, "verified.")

        for _warning in cls.warnings:
            cprint(colors.WARN, _warning)

    @classmethod
    def exit(cls):
        sys.exit(1 if cls.errors else 0)


def error(description):
    Verification.error(description)

def warning(description):
    Verification.warning(description)


def check_keys(data, required_keys, json_name=None):
    key_not_found = False
    for key in required_keys:
        if key not in data:
            if json_name:
                error('{} is required in {}'.format(key, json_name))
            else:
                error('{} is required'.format(key))
            key_not_found = True
    if key_not_found:
        raise KeyError


def error_on_duplicate_keys(ordered_pairs):
    data = {}
    for key, value in ordered_pairs:
        if key in data:
            error("duplicate key: {}".format(key))
        else:
            data[key] = value
    return data


def load_data(json_file, required_keys=()):
    try:
        with open(json_file, 'r') as f:
            try:
                data = json.load(f, object_pairs_hook=error_on_duplicate_keys)
            except ValueError:
                error('invalid json')
                return None
    except IOError:
        error('file does not exist')
        return None
    try:
        check_keys(data, required_keys)
    except KeyError:
        return None
    return data


def has_ending(file_name, endings):
    if isinstance(endings, string_types):
        endings = [endings]
    return any(file_name.endswith(ending) for ending in endings)

def is_ignored(file_name):
    return has_ending(file_name, ['.exe', '.class', '~', '.compile.out'])

def get_list_of_files(directory):
    return list(os.listdir(directory))


def check_identifier_format(var_name, var_value):
    try:
        if not re.match("[_A-Za-z][_a-zA-Z0-9]*$", var_value):
            error('{} must be a valid identifier: "{}"'.format(var_name, var_value))
    except Exception as exc:
        error(exc)


def verify_problem():
    # Checking existence/correctness of task properties...
    try:
        prob.short_name()
    except Exception as exc:
        error(exc)

    try:
        prob.title()
    except Exception as exc:
        error(exc)

    try:
        task_type = prob.task_type()
    except Exception as exc:
        error(exc)

    try:
        prob.has_manager()
    except Exception as exc:
        error(exc)

    try:
        prob.has_checker()
    except Exception as exc:
        error(exc)

    try:
        prob.has_grader()
    except Exception as exc:
        error(exc)

    check_identifier_format("grader_name", prob.grader_name())
    check_identifier_format("public_grader_name", prob.public_grader_name())

    try:
        prob.num_sol_processes()
    except Exception as exc:
        error(exc)

    try:
        time_limit = prob.time_limit()
        if time_limit < 0.5:
            error('time_limit should be a number greater or equal to 0.5')
    except Exception as exc:
        error(exc)

    try:
        memory_limit = prob.memory_limit()
        if memory_limit & (memory_limit - 1) != 0:
            warning('memory_limit is not a power of two')
    except Exception as exc:
        error(exc)

    if prob.task_type() == prob.TASK_TYPE__COMMUNICATION:
        try:
            prob.user_communication_policy()
        except Exception as exc:
            error(exc)


    def check_problem_name(prob_name):
        if not git_enabled or WEB_TERMINAL:
            return
        try:
            subprocess.check_output(["git", "--version"], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            warning('git command is not available')
            return
        try:
            subprocess.check_output(["git", "status"], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            warning('not a git repository')
            return
        try:
            git_main_remote_url = subprocess.check_output(["git", "config", "--local", "remote.{}.url".format(git_remote_name)], stderr=subprocess.STDOUT).strip().decode('utf-8')
            if '/' not in git_main_remote_url:
                warning('invalid syntax in git remote url: "{}"'.format(git_main_remote_url))
                return
            git_main_remote_name = os.path.basename(git_main_remote_url)
            if git_main_remote_name.endswith(".git"):
                git_main_remote_name = git_main_remote_name[:-4]
        except subprocess.CalledProcessError:
            warning('could not get git remote url for "{}"'.format(git_remote_name))
            return
        if prob_name != git_main_remote_name:
            warning('problem name and git project name are not the same')

    check_problem_name(prob.short_name())

    if prob.has_markdown_statement():
        try:
            with open(os.path.join(STATEMENT_DIR, 'index.md'), 'r') as f:
                first_line = None
                for line in f.readlines():
                    if line.strip() != '':
                        first_line = line
                        break

                if first_line is None:
                    warning('statement is empty')
                elif not first_line.strip().startswith('#'):
                    warning('statement does not start with a title')
                else:
                    statement_title = first_line.replace('#', '').strip()
                    if statement_title != prob.title():
                        warning('title (%s) does not match title in statement (%s)' % (prob.title(), statement_title))
        except IOError:
            warning('statement does not exist')

    if task_type not in prob.VALID_TASK_TYPES:
        error('type should be one of {}'.format('/'.join(prob.VALID_TASK_TYPES)))

    if task_type == prob.TASK_TYPE__OUTPUT_ONLY and prob.has_grader():
        warning('output only problems could not have grader')

    if prob.is_given('num_processes'):
        if task_type != prob.TASK_TYPE__COMMUNICATION:
            warning('"num_processes" is only used in communication tasks')

    if prob.is_given('grader_name'):
        if not prob.has_grader():
            warning('grader_name is given while the task does not have grader')

    if task_type == prob.TASK_TYPE__COMMUNICATION and not prob.has_manager():
        warning('communication problems must have manager')
    if task_type == prob.TASK_TYPE__OUTPUT_ONLY and prob.has_manager():
        warning('output only problems could not have manager')


def verify_subtasks():
    subtasks_data = load_data(SUBTASKS_JSON, ['subtasks'])

    if subtasks_data is None:
        return None

    k_glob = 'global_validators'
    k_sub = 'subtask_sensitive_validators'
    if (k_glob not in subtasks_data) and (k_sub not in subtasks_data):
        error('Neither "{}" nor "{}" is present in "{}".'.format(k_glob, k_sub, SUBTASKS_JSON_RELATIVE))
        return None

    validator_files = get_list_of_files(VALIDATOR_DIR)
    used_validators = set()

    def check_validator_key(parent, key, name, parName=None):
        if key not in parent:
            return
        validators_list = parent[key]
        parLoc = '' if parName is None else ' in "{}"'.format(parName)
        if not isinstance(validators_list, list):
            error('"{}" is not an array{}'.format(key, parLoc))
            return
        for index, validator_cmd_line in enumerate(validators_list):
            if not isinstance(validator_cmd_line, string_types):
                error('{} validator #{} is not a string{}'.format(name, index+1, parLoc))
                continue
            validator_cmd = validator_cmd_line.split(' ')[0]
            if '.' in validator_cmd:
                if validator_cmd not in validator_files:
                    error('File not found for {} validator "{}"{}'.format(name, validator_cmd, parLoc))
                else:
                    used_validators.add(validator_cmd)


    check_validator_key(subtasks_data, k_glob, 'global')
    check_validator_key(subtasks_data, k_sub, 'subtask-sensitive')

    subtask_placeholder_var = "subtask"
    subtask_placeholder_substitute = "___SUBTASK_PLACEHOLDER_SUBSTITUTE___"
    for subtask_sensitive_validator in subtasks_data.get(k_sub, []):
        try:
            subtask_validator_substituted = subtask_sensitive_validator.format(**{
                subtask_placeholder_var : subtask_placeholder_substitute
            })
        except KeyError as e:
            error('Subtask-sensitive validator "{}" contains unknown placeholder {{{}}}.'.format(subtask_sensitive_validator, e.args[0]))
        else:
            if subtask_placeholder_substitute not in subtask_validator_substituted:
                error('Subtask-sensitive validator "{}" does not contain the subtask placeholder {{{}}}.'.format(subtask_sensitive_validator, subtask_placeholder_var))

    subtasks = subtasks_data['subtasks']
    hasSamples = False
    try:
        if prob.task_type() != prob.TASK_TYPE__OUTPUT_ONLY:
            check_keys(subtasks, ['samples'])
            hasSamples = True
    except KeyError:
        pass

    indexes = set()
    score_sum = 0

    for name, data in subtasks.items():
        if not isinstance(data, dict):
            error('invalid data in {}'.format(name))
            continue

        try:
            check_keys(data, ['index', 'score'], name)
        except KeyError:
            continue

        indexes.add(data['index'])

        if not isinstance(data['score'], int) or data['score'] < 0:
            error('score should be a non-negative integer in subtask {}'.format(name))
        elif name == 'samples':
            if data['score'] != 0:
                error('samples subtask score is non-zero')
        else:
            score_sum += data['score']

        check_validator_key(data, 'validators', 'subtask', name)

    for unused_validator in set(validator_files) - used_validators - {'Makefile'}:
        if not is_ignored(unused_validator) and not has_ending(unused_validator, [".h"]):
            warning('Unused validator file "{}"'.format(unused_validator))

    if score_sum != 100:
        error('sum of scores is {}'.format(score_sum))

    for i in range(len(subtasks)):
        if i+(0 if hasSamples else 1) not in indexes:
            error('missing index {} in subtask indexes'.format(i))

    return subtasks


def verify_gen_data(subtasks):
    class GenDataVisitor(DataVisitor):
        def __init__(self):
            DataVisitor.__init__(self)
            self.tests_map = dict()
            self.subtasks = []
            self.testsets = []
            self.used_testsets = set()

        def on_testset(self, testset_name, line_number):
            self.testsets.append(testset_name)
            self.tests_map[testset_name] = set()

        def on_subtask(self, subtask_name, line_number):
            self.subtasks.append(subtask_name)
            self.used_testsets.add(subtask_name)

        def on_include(self, testset_name, included_testset, line_number):
            self.used_testsets.add(included_testset)
            self.tests_map[testset_name] |= self.tests_map[included_testset]

        def on_test(self, testset_name, test_name, line, line_number):
            self.tests_map[testset_name].add(test_name)


    gen_data = GenDataVisitor()
    try:
        with open(GEN_DATA, 'r') as f:
            try:
                parse_data_or_throw(f.readlines(), gen_data)
            except DataParseError as e:
                error(e.message)
                return
    except IOError:
        error('file does not exist or is not readable')
        return

    json_subtasks = set(subtasks.keys())
    gen_subtasks = set(gen_data.subtasks)
    #Checking the equivalence of subtasks in json file and data file:
    for s in json_subtasks-gen_subtasks:
        error("subtask '{}' is defined in '{}' but not mentioned in '{}'".format(s, SUBTASKS_JSON_RELATIVE, GEN_DATA_RELATIVE))
    for s in gen_subtasks-json_subtasks:
        error("subtask '{}' is mentioned in '{}' but not defined in '{}'".format(s, GEN_DATA_RELATIVE, SUBTASKS_JSON_RELATIVE))

    #Checking for empty testsets/subtasks:
    for testset in gen_data.testsets:
        if not gen_data.tests_map[testset]:
            if testset in gen_subtasks:
                score = 0
                if testset in subtasks:
                    score = subtasks[testset]['score']
                if score > 0:
                    error("subtask '{}' (with a positive score) has no tests".format(testset))
                else:
                    warning("subtask '{}' has no tests".format(testset))
            else:
                warning("testset '{}' has no tests".format(testset))

    #Checking if a testset is defined but not used:
    for ts in set(gen_data.testsets)-set(gen_data.used_testsets):
        warning("testset '{}' is not used anywhere".format(ts))


def verify_verdict(verdict, key_name):
    if not isinstance(verdict, string_types) or not verdicts.is_valid(verdict):
        error(
            "Verdict for '{}' is '{}', but it should be one of {{{}}} or their aliases"
            .format(key_name, verdict, ", ".join(verdicts.ALL_VERDICTS))
        )
        return False
    return True


def verify_solutions(subtasks):
    solutions = load_data(SOLUTIONS_JSON)
    if solutions is None or subtasks is None:
        return solutions

    model_solution = None
    solution_files = get_list_of_files(SOLUTION_DIR)
    used_solutions = set()

    for solution in solutions:
        if solution not in solution_files:
            error('{} does not exist'.format(solution))
            continue
        used_solutions.add(solution)

        data = solutions[solution]

        try:
            check_keys(data, ['verdict'], solution)
        except KeyError:
            continue

        verified = verify_verdict(data['verdict'], solution)
        if verified and verdicts.is_model_solution(data['verdict']):
            if model_solution is not None:
                error('there is more than one model solutions')
            model_solution = solution

        if 'except' in data:
            exceptions = data['except']
            if not isinstance(exceptions, dict):
                error('invalid except format in {}'.format(solution))
            else:
                for subtask_verdict in exceptions:
                    if subtask_verdict not in subtasks:
                        error('subtask "{}" is not defined and cannot be used in except'.format(subtask_verdict))
                    else:
                        verify_verdict(exceptions[subtask_verdict], '{}/except/{}'.format(solution, subtask_verdict))

    if model_solution is None:
        error('there is no model solution')

    for unused_solution in set(solution_files) - used_solutions:
        if not is_ignored(unused_solution):
            warning('{} is not represented'.format(unused_solution))

    return solutions


def verify_existence(files):
    for file0 in files:
        file = get_relative(file0)
        if not os.path.isfile(os.path.join(BASE_DIR, file)):
            error(file)

def verify_existence_warn(files):
    for file0 in files:
        file = get_relative(file0)
        if not os.path.isfile(os.path.join(BASE_DIR, file)):
            warning(file)


def verify():
    Verification.namespace = get_relative(PROBLEM_JSON)
    verify_problem()

    Verification.namespace = SUBTASKS_JSON_RELATIVE
    subtasks = verify_subtasks()

    Verification.namespace = GEN_DATA_RELATIVE
    verify_gen_data(subtasks)

    Verification.namespace = get_relative(SOLUTIONS_JSON)
    verify_solutions(subtasks)

    Verification.namespace = 'not found'
    verify_existence(necessary_files)
    verify_existence_warn(semi_necessary_files)

    Verification.report()
    Verification.exit()


if __name__ == "__main__":
    verify()
