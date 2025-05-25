import sys

from util import simple_usage_message, value_to_bash_str, write_exception_messages
import problem_model as prob


def get_problem_data(property_name):
    if not isinstance(property_name, str):
        raise ValueError(
            "Given argument '{}' is not a string"
            .format(property_name)
        )
    if not prob.is_public_property(property_name):
        raise ValueError(
            "Trying to access private members of the problem model using the argument '{}'"
            .format(property_name)
        )
    if property_name.startswith("general_property"):
        raise ValueError(
            "For generally getting a property from 'problem.json', use format '@property_name'"
        )

    if property_name.startswith("@"):
        return prob.general_property(property_name[1:])

    try:
        attr = getattr(prob, property_name)
    except AttributeError:
        raise ValueError(
            "No property '{}' in the problem model"
            .format(property_name)
        )
    if callable(attr):
        attr = attr()
    return attr


if __name__ == '__main__':
    if len(sys.argv) != 2:
        simple_usage_message("<property-name>|@<property-name>")

    try:
        value = get_problem_data(sys.argv[1])
        print(value_to_bash_str(value))
    except Exception as exc:
        write_exception_messages(exc)
        sys.exit(4)
