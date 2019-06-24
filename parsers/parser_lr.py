from grammar import Grammar, Item, ContainerSet
from .parser_abstract import Parser, ShiftReduceParser
from automaton import State
from .parser_tools import compute_firsts, compute_follows
from tools import multiline_formatter

class LR0(ShiftReduceParser):
    pass


class LR1(ShiftReduceParser):
    def _expand(self, item: Item):
        next_symb = item.NextSymbol
        if next_symb is None or not next_symb.IsNonTerminal:
            return []

        lookaheads = ContainerSet()
        for preview in item.Preview():
            lookaheads.hard_update(self._compute_local_first(preview))
        assert not lookaheads.contains_epsilon
        return [[Item(p, 0, lookaheads)] for p in next_symb.productions]

    def _compress(self, items):
        centers = {}
        for item in items:
            center = item.Center()
            try:
                lookahead = centers[center]
            except KeyError:
                lookahead = centers[center] = set()
            lookahead.update(item.lookaheads)

        return {Item(x.production, x.pos, set(lookahead)) for x, lookahead in centers.items()}

    def _closure(self, items):
        closure = ContainerSet(*items)

        changed = True
        while changed:
            changed = False

            new_items = ContainerSet()
            for item in closure:
                exp = self._expand(item)
                new_items.extend(exp)
            changed = closure.update(new_items)
        return self._compress(closure)

    def _goto(self, state, sym, only_kernel=False):
        items = frozenset(item.NextItem() for item in state if item.NextSymbol == sym)
        return items if only_kernel else self._closure(items)

    def _build_automaton(self):
        assert self.G.IsAugmentedGrammar, "Grammar must be augmented"

        self._firsts = compute_firsts(self.G)
        self._follows = compute_follows(self.G, self.firsts)

        self.firsts[self.EOF] = ContainerSet(self.EOF)
        self.Items = {}

        start_prod = self.startSymbol.productions[0]
        start_item = Item(start_prod, 0, lookaheads=(self.EOF,))
        start = frozenset([start_item])

        closure = self._closure(start)
        automaton = State(frozenset(closure), True)

        pending = [start]
        visited = {start: automaton}

        while pending:
            current = pending.pop()
            cur_state = visited[current]

            for sym in self.nonTerminals + self.terminals:
                kernels = self._goto(cur_state.state, sym, only_kernel=True)
                if not kernels:
                    continue
                try:
                    next_state = visited[kernels]
                except:
                    pending.append(kernels)
                    next_state = visited[kernels] = State(
                        frozenset(self._goto(cur_state.state, sym)), True
                    )

                cur_state.add_transition(sym.Name, next_state)

        automaton.set_formatter(multiline_formatter)
        self.automaton = automaton
        return automaton

    def str_conflictive_strings(self):
        return self.Errors

    def _build_table(self):
        is_lr1 = True
        errors = ""
        for i, node in enumerate(self.automaton):
            # print(i, "\t", "\n\t ".join(str(x) for x in node.state), "\n")
            node.idx = i
            node.tag = f'I{i}'

        for node in self.automaton:
            idx = node.idx
            for item in node.state:

                if item.IsReduceItem:
                    prod = item.production
                    if prod.Left == self.startSymbol:  # estado final
                        is_lr1 &= self._register(
                            self.ACTION, idx, self.EOF.Name, (ShiftReduceParser.OK, "")
                        )
                    else:
                        for lookahead in item.lookaheads:
                            is_lr1 &= self._register(
                                self.ACTION, idx, lookahead.Name, (ShiftReduceParser.REDUCE, prod)
                            )
                            errors += (
                                self._conflict_on(self.ACTION, idx, lookahead) if not is_lr1 else ""
                            )

                elif not item.NextSymbol.IsEpsilon:
                    next_sym = item.NextSymbol
                    if next_sym.IsTerminal:
                        try:
                            is_lr1 &= self._register(
                                self.ACTION,
                                idx,
                                next_sym.Name,
                                (ShiftReduceParser.SHIFT, node[next_sym.Name][0].idx),
                            )
                            errors += (
                                self._conflict_on(self.ACTION, idx, next_sym) if not is_lr1 else ""
                            )
                        except:
                            is_lr1 = False
                    else:  # nonterminal
                        is_lr1 &= self._register(
                            self.GOTO, idx, next_sym.Name, node[next_sym.Name][0].idx
                        )
                        errors += self._conflict_on(self.GOTO, idx, next_sym) if not is_lr1 else ""
        self.Errors = errors
        self._parse_corrupted = not is_lr1
        self.automaton.set_formatter(multiline_formatter)


    def format_recognize(self, output: list, info: str):
        return bool(output), info

    # def _str_conflicts(self):
    #     return self.Errors  # TODO: Conflictives words

    # def _str_tables(self):
    #     str_res = " Action:"
    #     for X in self.ACTION:
    #         str_res += f"\n  State<{X}>:"
    #         for symb, vals in self.ACTION[X].items():
    #             if vals:
    #                 str_res += (
    #                     f"\n    [{symb}] -> "
    #                     + "["
    #                     + ", ".join(
    #                         (
    #                             f"{val[0]}: State<{val[1]}>"
    #                             if val[0] == LR1.SHIFT
    #                             else (
    #                                 f"{val[0]}: Prod({repr(val[1])})"
    #                                 if val[0] == LR1.REDUCE
    #                                 else f"{val[0]}"
    #                             )
    #                         )
    #                         for val in vals
    #                     )
    #                     + "]"
    #                     + ("  (conflicto)" if conflict_cond_lr1(vals) else "")
    #                 )
    #     str_res += "\n\n Goto:"
    #     for X in self.GOTO:
    #         str_res += f"\n  State<{X}>:"
    #         for symb, vals in self.GOTO[X].items():
    #             if vals:
    #                 str_res += (
    #                     f"\n    [{symb}] -> "
    #                     + "["
    #                     + ", ".join(
    #                         (f"State<{val[1]}>" if isinstance(val, tuple) else f"State<{val}> ")
    #                         for val in vals
    #                     )
    #                     + "]"
    #                     + ("  (conflicto)" if conflict_cond_lr1(vals) else "")
    #                 )

    #     str_res += "\n"

        # return str_res


def conflict_cond_lr1(cell: list):
    if isinstance(cell, list) and len(cell) in (0, 1):
        return False
    return len(cell) > 1 and sum(map(lambda x: 0 if x[0] == LR1.SHIFT else 1, cell)) != 0
