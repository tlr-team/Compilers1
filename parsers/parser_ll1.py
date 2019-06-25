from .parser_abstract import Parser, corrupt_protection
from .parser_tools import compute_firsts, compute_follows, compute_local_first
from grammar import Grammar
from tools import table_to_dataframe, pretty_table


class LL1(Parser):
    def _build_parser(self):
        table = {}
        is_ll1 = True

        for production in self.productions:
            X = production.Left
            alpha = production.Right

            for symbol in self.firsts[alpha]:
                is_ll1 &= self._register(table, X, symbol, production)

            if production.IsEpsilon:
                for sym in self.follows[X]:
                    is_ll1 &= self._register(table, X, sym, production)

        self.table = table
        self._parse_corrupted = not is_ll1

    def __call__(self, word, verbose=True):
        """
            Parse a word.
        """

        stack = [self.startSymbol]
        cursor = 0
        output = []
        verbosity = ""
        ###################################################
        try:
            assert not self.parse_corrupted

            while True:
                top = stack.pop()
                a = word[cursor]

                if top.IsTerminal:
                    if a == top:
                        cursor += 1
                    else:
                        return False, output, verbosity

                elif top.IsNonTerminal:
                    production = self.table[top][a][0]
                    if production != None:
                        if verbose:
                            verbosity += f"stack: {str(stack)}\n( {repr(production)} ) - ( {' '.join(str(s) for s in word[cursor:])} )\n\n"

                        alpha = production.Right
                        output.append(production)
                        for i in range(len(alpha)):
                            stack.append(alpha[-i - 1])
                    else:
                        assert False, "Something wrong."

                if len(stack) == 0:
                    break
        except:
            return False, output, "parser no disponible" + verbosity
        return True, output, verbosity

    def _str_conflicts(self):
        str_res = ""
        for X in self.table:
            str_res += (
                (
                    f"\n  {X}:"
                    + "\t".join(
                        f"\n    [{symb}] -> Prod{vals}{('  (conflicto)')}"
                        for symb, vals in self.table[X].items()
                        if len(vals) > 1
                    )
                )
                if any(len(vals) > 1 for symb, vals in self.table[X].items())
                else ""
            )
        str_res = "\n CONFLICTOS:\n" + str_res if str_res else ""

        return str_res

    def _str_tables(self):
        str_res = "\n < TABLE > \n" + str(pretty_table(self.G, self.table))

        return str_res
