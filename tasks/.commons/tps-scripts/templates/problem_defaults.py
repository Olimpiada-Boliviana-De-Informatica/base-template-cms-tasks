import problem_model as prob

# Default values for the problem properties defined in problem_model.
# A property here must have exactly the same name as in problem_model.
# For setting a defult value for a problem property,
#  you can define the property as a simple variable,
#  or define it as a function which will be called when looking up for the default value.
# If a default value is not set for a property here,
#  setting its value (generally in problem.json) is considered to be mandatory.


def title():
    return prob.short_name()

def code():
    return prob.short_name()

# web_url = ""

verify_git = False


# def task_type():
#     return prob.TASK_TYPE__BATCH

def has_manager():
    return prob.task_type() == prob.TASK_TYPE__COMMUNICATION

def has_checker():
    return prob.task_type() != prob.TASK_TYPE__COMMUNICATION

def has_grader():
    return prob.task_type() != prob.TASK_TYPE__OUTPUT_ONLY

grader_name = "grader"

def public_grader_name():
    return prob.grader_name()

num_sol_processes = 1

def user_communication_policy():
    return prob.USER_COMMUNICATION_POLICY__STDIO

score_precision = 4


# time_limit = 1.00
# seconds

# memory_limit = 2048
# MiB


cpp_enabled = True

java_enabled = False

pascal_enabled = False

python_enabled = False


cpp_std = "gnu++20"

cpp_warning_flags = "-Wall -Wextra -Wshadow"

cpp_optimization_flags = "-O2"

cpp_extra_compile_flags = "-DEVAL"
