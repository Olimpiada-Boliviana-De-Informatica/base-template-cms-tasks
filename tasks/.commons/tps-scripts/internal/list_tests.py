import sys

from util import simple_usage_message
from tests_util import get_test_names_by_gen_data


if __name__ == '__main__':
    if len(sys.argv) != 2:
        simple_usage_message("<gen-data-file>")
    gen_data_file = sys.argv[1]

    with open(gen_data_file, 'r') as gdf:
        gen_data = gdf.readlines()
    tests = get_test_names_by_gen_data(gen_data)

    for test in tests:
        print(test)
