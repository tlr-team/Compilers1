from functools import wraps
from grammar import Grammar
from .parser_tools import compute_firsts, compute_follows, compute_local_first


def corrupt_protection(func):
    @wraps
    def wrapper(*args, **kwargs):
        if args[0].parse_corrupted:
            return
        return func(*args, **kwargs)
    return wrapper


class Parser:
    OK = "ok"
    ERROR = "error"

    def __init__(self, G: Grammar, firsts=None, follows=None):
        self.G = G.copy()
        self._firsts = firsts
        self._follows = follows
        self._parse_corrupted = None
        self._build_parser()

    @property
    def parse_corrupted(self):
        return self._parse_corrupted

    @property
    def firsts(self):
        if not self._firsts:
            self._firsts = compute_firsts(self.G)
        return self._firsts

    @property
    def follows(self):
        if not self._firsts:
            self._firsts = compute_firsts(self.G)
        if not self._follows:
            self._follows = compute_follows(self.G, self.firsts)
        return self._follows

    @property
    def terminals(self):
        return self.G.terminals

    @property
    def nonTerminals(self):
        return self.G.nonTerminals

    @property
    def productions(self):
        return self.G.Productions

    @property
    def startSymbol(self):
        return self.G.startSymbol

    @property
    def Epsilon(self):
        return self.G.Epsilon

    @property
    def EOF(self):
        return self.G.EOF

    def _compute_local_first(self, alpha):
        """ 
        Computes First(alpha), given First(Vt) and First(Vn)
        alpha in (Vt U Vn)*
        """
        return compute_local_first(self.firsts, alpha)

    def _build_parser(self):
        """
        Build table and automaton.
        """
        self._build_table()
        self._build_automaton()

    # ToImplement
    def _build_table(self):
        """
            This method must be hided for another implementation.
        """
        raise NotImplementedError

    def _build_automaton(self):
        """
            This method must be hided for another implementation.
        """
        raise NotImplementedError

    def _str_conflicts(self):
        """
            This method must be hided for another implementation.
        """
        raise NotImplementedError

    def _str_tables(self):
        """
            This method must be hided for another implementation.
        """
        raise NotImplementedError
    
    def __call__(self, word):
        """
            Parse a word.\n
            `This method must be hided for another implementation`
        """
        raise NotImplementedError
    
    @corrupt_protection
    @property
    def svg_automaton(self):
        """
            Returns an image in svg format.\n
            `This method must be hided for another implementation`
        """
        raise NotImplementedError
    # EndToImplement

    def _add_transition(self, table, X, sym, val):
        table[X] = table[X] if X in table else {}
        table[X][sym] = table[X][sym] if sym in table[X] else []

        if val not in table[X][sym]:
            table[X][sym].append(val)

        return len(table[X][sym]) == 1

    def __str__(self):
        """
            Returns an string that contains info about\n 
            the gramar with the especific parser.\n
            `Don't override this method`
        """
        if self.parse_corrupted is None:
            return f"Not initialized {type(self).__name__}"
        elif self._parse_corrupted:
            return (
                f"No es {type(self).__name__}: \n{self._str_tables()}\n{self._str_conflicts()}\n"
            )
        else:
            return f"Es {type(self).__name__}: \n{self._str_tables()}\n"

    # __repr__ = str(__name__)


class ShiftReduceParser(Parser):
    SHIFT = "shift"
    REDUCE = "reduce"

    def __init__(self, G: Grammar, firsts=None, follows=None):
        self.Items = {}
        self.CanonicalCollection = []
        self.ACTION = {}
        self.GOTO = {}

        super().__init__(G.AugmentedGrammar(), firsts=firsts, follows=follows)

    @corrupt_protection
    def __call__(self, word, verbose=False):
        """
            Recognize a word or not.
        """
        stack = [0]
        pointer = 0
        output = []
        productions = ""

        while True:
            state = stack[-1]
            lookahead = word[pointer]
            try:
                action, tag = self.ACTION[state][lookahead][0]

                if verbose:
                    productions += str(stack) + str(word[pointer:]) + "\n"

                if action == ShiftReduceParser.SHIFT:
                    stack.append(tag)
                    pointer += 1
                elif action == ShiftReduceParser.REDUCE:
                    for _ in range(len(tag.Right)):
                        stack.pop()
                    stack.append(self.GOTO[stack[-1]][tag.Left][0])
                    output.append(tag)
                elif action == ShiftReduceParser.OK:
                    output.reverse()
                    return output, productions
                else:
                    assert False, "Must be something wrong!"
            except KeyError:
                return None, None

    def _conflict_on(self, table, X, symbol):
        if X in table and symbol in table[X] and len() == 2:
            return f"Conflicto:\n\t( {table[X][symbol][0][0]} - {table[X][symbol][1][0]}, Estado: {X}, Símbolo: {symbol} )\n"
        return ""
