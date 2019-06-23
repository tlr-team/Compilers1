from parsers import LR1


def conflict_cond_ll1(cell: list):
    return isinstance(cell, list) and len(cell) > 1


def conflict_cond_lr1(cell: list):
    if isinstance(cell, list) and len(cell) in (0, 1):
        return False
    return len(cell) > 1 and sum(map(lambda x: 0 if x[0] == LR1.SHIFT else 1, cell)) != 0
