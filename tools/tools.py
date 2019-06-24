from pandas import DataFrame

SHIFT = "shift"
REDUCE = "reduce"
OK = "ok"
ERROR = "error"

def multiline_formatter(state):
    return '\n'.join(str(item) for item in state)

def conflict_cond_ll1(cell: list):
    return isinstance(cell, list) and len(cell) > 1


def encode_value(value):
    try:
        action, tag = value
        if action == SHIFT:
            return "S" + str(tag)
        elif action == REDUCE:
            return repr(tag)
        elif action == OK:
            return action
        else:
            return repr(value)
    except TypeError:
        return repr(value)


def table_to_dataframe(table):
    d = {}
    for state in table:
        for symbol in table[state]:
            value = encode_value(table[state][symbol][0])
            try:
                d[state][symbol] = value
            except KeyError:
                d[state] = {symbol: value}

    return DataFrame.from_dict(d, orient="index", dtype=str)

