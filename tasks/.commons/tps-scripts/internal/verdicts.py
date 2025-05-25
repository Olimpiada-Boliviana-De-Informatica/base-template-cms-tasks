
VERDICT__MODEL_SOLUTION = "model_solution"
VERDICT__CORRECT = "correct"
VERDICT__PARTIALLY_CORRECT = "partially_correct"
VERDICT__INCORRECT = "incorrect"
VERDICT__TIME_LIMIT_EXCEEDED = "time_limit"
VERDICT__MEMORY_LIMIT_EXCEEDED = "memory_limit"
VERDICT__RUNTIME_ERROR = "runtime_error"
VERDICT__PROTOCOL_VIOLATION = "protocol_violation"
VERDICT__SECURITY_VIOLATION = "security_violation"

ATOMIC_VERDICTS = [
    VERDICT__MODEL_SOLUTION,
    VERDICT__CORRECT,
    VERDICT__PARTIALLY_CORRECT,
    VERDICT__INCORRECT,
    VERDICT__TIME_LIMIT_EXCEEDED,
    VERDICT__MEMORY_LIMIT_EXCEEDED,
    VERDICT__RUNTIME_ERROR,
    VERDICT__PROTOCOL_VIOLATION,
    VERDICT__SECURITY_VIOLATION,
]


VERDICTS__CORRECT_MODEL = [
    VERDICT__CORRECT,
    VERDICT__MODEL_SOLUTION,
]

VERDICTS__TLE_RTE = [
    VERDICT__TIME_LIMIT_EXCEEDED,
    VERDICT__RUNTIME_ERROR,
]

VERDICT__FAILED = "failed"
VERDICT__TLE_RTE = "time_limit_and_runtime_error"

COMPOUND_VERDICTS = {
    VERDICT__FAILED : [v for v in ATOMIC_VERDICTS if v not in VERDICTS__CORRECT_MODEL],
    VERDICT__TLE_RTE : VERDICTS__TLE_RTE,
}


ALL_VERDICTS = ATOMIC_VERDICTS + list(COMPOUND_VERDICTS.keys())



def _mul(l1, l2):
    return [
        a1+a2
        for a1 in l1
        for a2 in l2
    ]

def _mul2(l1, l2):
    return [
        x
        for a1 in l1
        for a2 in l2
        for x in (a1+'_'+a2, a2+'_'+a1,)
    ]

ALIASES = {
    VERDICT__MODEL_SOLUTION:
        ["model",],
    VERDICT__CORRECT:
        ["ac", "accept", "accepted",],
    VERDICT__PARTIALLY_CORRECT:
        ["pc", "partial",],
    VERDICT__INCORRECT:
        ["wa", "wrong", "wronganswer", "wrong_answer",],
    VERDICT__TIME_LIMIT_EXCEEDED:
        ["tl", "tle", "time", "timelimit",] +
        _mul(["timelimit", "time_limit"], ["_exceed", "_exceeded"]),
    VERDICT__MEMORY_LIMIT_EXCEEDED:
        ["ml", "mle", "memory", "mem", "mem_limit",] +
        _mul(["mem_limit", "memory_limit"], ["_exceed", "_exceeded"]),
    VERDICT__RUNTIME_ERROR:
        ["rt", "re", "rte", "runtime", "run_time", "run_time_error",],
    VERDICT__PROTOCOL_VIOLATION:
        ["pv", "proto_viol",],
    VERDICT__SECURITY_VIOLATION:
        ["sv", "secur_viol",],
    VERDICT__FAILED:
        ["f", "fail",],
    VERDICT__TLE_RTE:
        _mul2(["tle", "tl"], ["rte", "rt", "re"]),
}


def _dict_no_dupl(it):
    result = {}
    for key, value in it:
        if key in result:
            raise ValueError("Duplicate key found: {}".format(key))
        result[key] = value
    return result

UNIFIED_ALIAS = _dict_no_dupl(
    (alias, verd)
    for verd, aliases in ALIASES.items()
    for alias in [verd,]+aliases
)


def get_unified(verdict):
    return UNIFIED_ALIAS.get(verdict.lower(), None)

def is_valid(text):
    return get_unified(text) is not None


def is_model_solution(verdict):
    return get_unified(verdict) == VERDICT__MODEL_SOLUTION




VERDICT_MESSAGE__CORRECT = "Correct"
VERDICT_MESSAGE__PARTIALLY_CORRECT = "Partially Correct"
VERDICT_MESSAGE__WRONG_ANSWER = "Wrong Answer"
VERDICT_MESSAGE__TIME_LIMIT_EXCEEDED = "Time Limit Exceeded"
VERDICT_MESSAGE__RUNTIME_ERROR = "Runtime Error"
VERDICT_MESSAGE__PROTOCOL_VIOLATION = "Protocol Violation"
VERDICT_MESSAGE__SECURITY_VIOLATION = "Security Violation"

VERDICT_MESSAGE__WRONG_ANSWER_INVALID_ARGS = "Output isn't correct: Invalid argument"
VERDICT_MESSAGE__WRONG_ANSWER_TOO_MANY_CALLS = "Output isn't correct: Too many calls"

def score_and_verdict_message_matches_expected(score, verdict_msg, expected_verdict):
    expected_verdict = get_unified(expected_verdict)
    if expected_verdict in VERDICTS__CORRECT_MODEL:
        return verdict_msg == VERDICT_MESSAGE__CORRECT and score == 1
    elif expected_verdict == VERDICT__INCORRECT:
        return verdict_msg == VERDICT_MESSAGE__WRONG_ANSWER or \
               verdict_msg == VERDICT_MESSAGE__WRONG_ANSWER_INVALID_ARGS or \
               verdict_msg == VERDICT_MESSAGE__WRONG_ANSWER_TOO_MANY_CALLS
    elif expected_verdict == VERDICT__TIME_LIMIT_EXCEEDED:
        return verdict_msg == VERDICT_MESSAGE__TIME_LIMIT_EXCEEDED
    elif expected_verdict == VERDICT__MEMORY_LIMIT_EXCEEDED:
        return verdict_msg == VERDICT_MESSAGE__RUNTIME_ERROR
    elif expected_verdict == VERDICT__RUNTIME_ERROR:
        return verdict_msg == VERDICT_MESSAGE__RUNTIME_ERROR
    elif expected_verdict == VERDICT__PROTOCOL_VIOLATION:
        return verdict_msg == VERDICT_MESSAGE__PROTOCOL_VIOLATION
    elif expected_verdict == VERDICT__SECURITY_VIOLATION:
        return verdict_msg == VERDICT_MESSAGE__SECURITY_VIOLATION
    elif expected_verdict == VERDICT__FAILED:
        return verdict_msg != VERDICT_MESSAGE__CORRECT or score == 0
    elif expected_verdict == VERDICT__TLE_RTE:
        return verdict_msg in [VERDICT_MESSAGE__TIME_LIMIT_EXCEEDED, VERDICT_MESSAGE__RUNTIME_ERROR]
    elif expected_verdict == VERDICT__PARTIALLY_CORRECT:
        return 0 < score < 1
    else:
        raise ValueError("Invalid verdict")
