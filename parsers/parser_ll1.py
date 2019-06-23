from .parser_abstract import Parser, corrupt_protection
from .parser_tools import compute_firsts, compute_follows, compute_local_first
from grammar import Grammar


class LL1(Parser):
    def __init__(self, G: Grammar, firsts=None, follows=None):
        super().__init__(G, firsts=firsts, follows=follows)

    def _build_parser(self):
        table = {}
        is_ll1 = True

        for production in self.productions:
            X = production.Left
            alpha = production.Right

            if not production.IsEpsilon:  # TODO: this 'if' is really necesary?
                for sym in self.firsts[alpha]:
                    is_ll1 &= self._add_transition(table, X, sym.Name, production)

            if production.IsEpsilon:
                for sym in self.follows[X]:
                    is_ll1 &= self._add_transition(table, X, sym.Name, production)

        self.table = table
        self._parse_corrupted = not is_ll1

    def __call__(self, word, verbose=True):
        """
            Parse a word.
        """

        stack = [self.startSymbol]
        cursor = 0
        output = []
        info = ""
        ###################################################
        try:
            assert not self.parse_corrupted

            while True:
                top = stack.pop()
                a = word[cursor]

                if top.IsTerminal:
                    if a == top.Name:
                        cursor += 1
                    else:
                        raise ("parsing error")

                elif top.IsNonTerminal:
                    production = self.table[top][a][0]
                    if production != None:
                        if verbose:
                            info += f"produccion: {production}, stack: {stack[:]}, palabra: {word[cursor:]}\n"

                        alpha = production.Right
                        output.append(production)
                        for i in range(len(alpha)):
                            stack.append(alpha[-i - 1])
                    else:
                        raise ("parsing error")

                if len(stack) == 0:
                    break
        except:
            return self.format_recognize([], "parser no disponible")
        return self.format_recognize(output, info if verbose else "\n" + "\n".join(output))

    def format_recognize(self, output: list, info: str):
        return bool(output), info

    def _str_conflicts(self):
        return ""

    def _str_tables(self):
        str_res = ""
        for X in self.table:
            str_res += f"\n  {X}:" + "\t".join(
                f"\n    [{symb}] -> {vals}{('  (conflicto)') if len(vals) > 1 else ('') }"
                for symb, vals in self.table[X].items()
                if vals
            )
        return str_res
