import problem_model as prob

def get_test_name(testset_name, testset_index, subtask_index, test_index, test_offset, gen_line): #pylint: disable=too-many-arguments
    #pylint: disable=unused-argument
    if prob.task_type() == prob.TASK_TYPE__OUTPUT_ONLY:
        return "%02d" % test_index
    return (testset_name if subtask_index < 0 else str(subtask_index)) + "-%02d" % test_offset
