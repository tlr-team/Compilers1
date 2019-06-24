from .parser_abstract import Parser, corrupt_protection
from .parser_tools import compute_firsts, compute_follows, compute_local_first
from grammar import Grammar
from tools import table_to_dataframe

class LL1(Parser):
    def _build_parser(self):
        table = {}
        is_ll1 = True

        for production in self.productions:
            X = production.Left.Name
            alpha = production.Right

            if not production.IsEpsilon:  # TODO: this 'if' is really necesary?
                for sym in self.firsts[alpha]:
                    is_ll1 &= self._register(table, X, sym.Name, production)

            if production.IsEpsilon:
                for sym in self.follows[X]:
                    is_ll1 &= self._register(table, X, sym.Name, production)

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
            return False,output, "parser no disponible"
        return True, output, verbose

    def format_recognize(self, output: list, info: str):
        return bool(output), info

    def _str_conflicts(self):
        str_res = "\n ---------------------- PARSER-CONFLICTOS --------------------------\n"
        for X in self.table:
            str_res += (f"\n  {X}:" + "\t".join(
                f"\n    [{symb}] -> Prod{vals}{('  (conflicto)')}"
                for symb, vals in self.table[X].items()
                if len(vals) > 1
            )) if any(len(vals) > 1 for symb, vals in self.table[X].items()) else ""
            
        return str_res

    def _str_tables(self):
        str_res = ("\n ---------------------- TABLE -------------------------- \n"
            + str(table_to_dataframe(self.table)))
    
        return str_res
