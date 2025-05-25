import sys as _sys
import os as _os
import inspect as _inspect

import util as _util
import json_extract as _json_extract
import problem_defaults as _defaults


def _restricted(func):
    func.is_restricted = True
    return func


@_restricted
def is_public_property(property_name):
    if property_name.startswith("_"):
        return False
    cur_mod = _sys.modules[__name__]
    if not hasattr(cur_mod, property_name):
        return False
    func = getattr(cur_mod, property_name)
    if not callable(func):
        return False
    if hasattr(func, 'is_restricted') and func.is_restricted:
        return False
    return True


PROBLEM_JSON = _os.environ.get('PROBLEM_JSON')

_problem_json_data = None

def _get_problem_json_data():
    global _problem_json_data
    if _problem_json_data is None:
        _problem_json_data = _util.load_json(PROBLEM_JSON)
    return _problem_json_data


def _extract_property_name_from_call_stack():
    for frame_info in _inspect.stack():
        if not frame_info.function.startswith("_"):
            return frame_info.function
    return None


def _probext(path, *args):
    _data = _get_problem_json_data()
    try:
        return _json_extract.navigate_json(_data, path, PROBLEM_JSON)
    except Exception as exc:
        if args:
            # default value is provided here as argument
            return args[0]
        property_name = _extract_property_name_from_call_stack()
        if property_name is None or not is_public_property(property_name):
            raise exc
        try:
            default_attr = getattr(_defaults, property_name)
        except AttributeError:
            # No value for property '{property_name}' in problem defaults
            raise exc
        default_value = default_attr() if callable(default_attr) else default_attr
        return default_value


@_restricted
def is_given(path):
    _data = _get_problem_json_data()
    try:
        _json_extract.navigate_json(_data, path, PROBLEM_JSON)
        return True
    except:
        return False


def _check_type(_type, value, name):
    if not isinstance(value, _type):
        raise Exception(
            "Invalid value '{}' in '{}'. Expected a value of type '{}'.)"
            .format(value, name, _type.__name__)
        )

def _probext_type(_type, path, *args):
    v = _probext(path, *args)
    if v is not None:
        _check_type(_type, v, path)
    return v


def _probext_str(path, *args):
    return _probext_type(str, path, *args)

def _probext_bool(path, *args):
    return _probext_type(bool, path, *args)

def _probext_int(path, *args):
    return _probext_type(int, path, *args)

def _probext_float(path, *args):
    return _probext_type(float, path, *args)


def _probext_str_enum(path, valid_options, *args):
    s = _probext_str(path, *args)
    if s not in valid_options:
        raise Exception(
            "Invalid value '{}' for '{}'. Expected a value among {{{}}}."
            .format(s, path, ", ".join(valid_options))
        )
    return s

def _probext_int_positive(path, *args):
    i = _probext_int(path, *args)
    if i <= 0:
        raise Exception(
            "Invalid value '{}' for '{}'. Expected a positive integer value."
            .format(i, path)
        )
    return i

def _probext_int_nonnegative(path, *args):
    i = _probext_int(path, *args)
    if i < 0:
        raise Exception(
            "Invalid value '{}' for '{}'. Expected a non-negative integer value."
            .format(i, path)
        )
    return i

def _probext_float_positive(path, *args):
    f = _probext_float(path, *args)
    if f <= 0:
        raise Exception(
            "Invalid value '{}' for '{}'. Expected a positive float value."
            .format(f, path)
        )
    return f


def general_property(property_name, *args):
    return _probext(property_name, *args)

def general_property_str(property_name, *args):
    return _probext_str(property_name, *args)

def general_property_bool(property_name, *args):
    return _probext_bool(property_name, *args)

def general_property_int(property_name, *args):
    return _probext_int(property_name, *args)

def general_property_float(property_name, *args):
    return _probext_float(property_name, *args)



def short_name():
    return _probext_str("name")

def title():
    return _probext_str("title")

def code():
    return _probext_str("code")

def web_url():
    return _probext_str("web_url")


def has_markdown_statement():
    #TODO read it from problem.json
    return True


def verify_git():
    return _probext_bool("verify_git")


TASK_TYPE__BATCH="Batch"
TASK_TYPE__COMMUNICATION="Communication"
TASK_TYPE__OUTPUT_ONLY="OutputOnly"
TASK_TYPE__TWO_STEPS="TwoSteps"

VALID_TASK_TYPES = [
    TASK_TYPE__BATCH,
    TASK_TYPE__COMMUNICATION,
    TASK_TYPE__OUTPUT_ONLY,
    TASK_TYPE__TWO_STEPS,
]

def task_type():
    return _probext_str_enum("type", VALID_TASK_TYPES)


def run_script_type_in_compilation():
    t = task_type()
    if t in [TASK_TYPE__BATCH, TASK_TYPE__OUTPUT_ONLY]:
        return "batch"
    if t == TASK_TYPE__COMMUNICATION:
        return "communication"
    if t == TASK_TYPE__TWO_STEPS:
        return "two-steps"
    return "other"



def has_manager():
    return _probext_bool("has_manager")


def has_checker():
    return _probext_bool("has_checker")


def has_grader():
    return _probext_bool("has_grader")


def grader_name():
    return _probext_str("grader_name")

def public_grader_name():
    return _probext_str("public_grader_name")


def num_sol_processes():
    return _probext_int_positive("num_processes")



# User processes communicate through stdin & stdout
USER_COMMUNICATION_POLICY__STDIO = "std_io"

# User processes communicate through fifo files whose paths are given as arguments
USER_COMMUNICATION_POLICY__FILE_ARGS = "fifo_io"

VALID_USER_COMMUNICATION_POLICIES = [
    USER_COMMUNICATION_POLICY__STDIO,
    USER_COMMUNICATION_POLICY__FILE_ARGS,
]

def user_communication_policy():
    """Specifies how the user processes interact with the manager in Communication tasks."""
    # Names are not ideal, but this is the CMS terminology.
    return _probext_str_enum("user_io", VALID_USER_COMMUNICATION_POLICIES)

def user_communicates_through_stdio():
    return user_communication_policy() == USER_COMMUNICATION_POLICY__STDIO

def user_communicates_through_file_args():
    return user_communication_policy() == USER_COMMUNICATION_POLICY__FILE_ARGS



def score_precision():
    """Score precision (#digits after decimal point, in partial scoring), assuming 0.0 <= score <= 1.0"""
    return _probext_int_nonnegative("score_precision")


def time_limit():
    """Unit: seconds"""
    return _probext_float_positive("time_limit")


def memory_limit():
    """Unit: MiB (2^20 bytes)"""
    return _probext_int_positive("memory_limit")


def cpp_enabled():
    return _probext_bool("cpp_enabled")

def java_enabled():
    return _probext_bool("java_enabled")

def pascal_enabled():
    return _probext_bool("pascal_enabled")

def python_enabled():
    return _probext_bool("python_enabled")


def cpp_std():
    env_cpp_std = _os.environ.get("CPP_STD_OPT")
    if env_cpp_std is not None:
        return env_cpp_std
    return _probext_str("cpp_std")

def cpp_std_flag():
    std = cpp_std()
    return "--std={}".format(std) if std else ""


def cpp_warning_flags():
    env_cpp_warnings = _os.environ.get("CPP_WARNING_OPTS")
    if env_cpp_warnings is not None:
        return env_cpp_warnings
    return _probext_str("cpp_warning_flags")


def cpp_optimization_flags():
    env_cpp_optimizations = _os.environ.get("CPP_OPTIMIZATION_FLAGS")
    if env_cpp_optimizations is not None:
        return env_cpp_optimizations
    return _probext_str("cpp_optimization_flags")


def cpp_extra_compile_flags():
    env_cpp_extra_compile_flags = _os.environ.get("CPP_EXTRA_COMPILE_FLAGS")
    if env_cpp_extra_compile_flags is not None:
        return env_cpp_extra_compile_flags
    return _probext_str("cpp_extra_compile_flags")
