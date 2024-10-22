import json


class ContainerSet:
    def __init__(self, *values, contains_epsilon=False):
        self.set = set(values)
        self.contains_epsilon = contains_epsilon

    def add(self, value):
        n = len(self.set)
        self.set.add(value)
        return n != len(self.set)

    def set_epsilon(self, value=True):
        last = self.contains_epsilon
        self.contains_epsilon = value
        return last != self.contains_epsilon

    def update(self, other):
        n = len(self.set)
        self.set.update(other.set)
        return n != len(self.set)

    def extend(self, values):
        change = False
        for value in values:
            change |= self.add(value)
        return change

    def epsilon_update(self, other):
        return self.set_epsilon(self.contains_epsilon | other.contains_epsilon)

    def hard_update(self, other):
        return self.update(other) | self.epsilon_update(other)

    def __len__(self):
        return len(self.set) + int(self.contains_epsilon)

    def __str__(self):
        return "%s%s" % (str(self.set), " - epsilon" if self.contains_epsilon else "")

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return iter(self.set)

    def __eq__(self, other):
        return (
            isinstance(other, ContainerSet)
            and self.set == other.set
            and self.contains_epsilon == other.contains_epsilon
        )

    def __nonzero__(self):
        return len(self) > 0

    def __contains__(self, item):
        item_epsilon = False
        try:
            item_epsilon = item.IsEpsilon
        except:
            pass
        if item_epsilon:
            return self.contains_epsilon

        return item in self.set

    def copy(self):
        return ContainerSet(self.set.copy(), contains_epsilon=self.contains_epsilon)


class Symbol(object):
    def __init__(self, name, grammar):
        self.Name = name
        self.Grammar = grammar

    def __str__(self):
        return self.Name

    def __repr__(self):
        return repr(self.Name)

    def __add__(self, other):
        if isinstance(other, Symbol):
            return Sentence(self, other)

        raise TypeError(other)

    def __or__(self, other):

        if isinstance(other, (Sentence)):
            return SentenceList(Sentence(self), other)

        raise TypeError(other)

    @property
    def IsEpsilon(self):
        return False

    def __len__(self):
        return 1


class NonTerminal(Symbol):
    def __init__(self, name, grammar):
        super().__init__(name, grammar)
        self.productions = []

    def __imod__(self, other):

        if isinstance(other, (Sentence)):
            p = Production(self, other)
            self.Grammar.Add_Production(p)
            return self

        if isinstance(other, tuple):
            assert len(other) == 2, "Tiene que ser una Tupla de 2 elementos (sentence, attribute)"

            if isinstance(other[0], Symbol):
                p = AttributeProduction(self, Sentence(other[0]), other[1])
            elif isinstance(other[0], Sentence):
                p = AttributeProduction(self, other[0], other[1])
            else:
                raise Exception("")

            self.Grammar.Add_Production(p)
            return self

        if isinstance(other, Symbol):
            p = Production(self, Sentence(other))
            self.Grammar.Add_Production(p)
            return self

        if isinstance(other, SentenceList):

            for s in other:
                p = Production(self, s)
                self.Grammar.Add_Production(p)

            return self

        raise TypeError(other)

    @property
    def IsTerminal(self):
        return False

    @property
    def IsNonTerminal(self):
        return True

    @property
    def IsEpsilon(self):
        return False


class Terminal(Symbol):
    def __init__(self, name, grammar):
        super().__init__(name, grammar)

    @property
    def IsTerminal(self):
        return True

    @property
    def IsNonTerminal(self):
        return False

    @property
    def IsEpsilon(self):
        return False


class EOF(Terminal):
    def __init__(self, Grammar):
        super().__init__("$", Grammar)


class Sentence(object):
    def __init__(self, *args):
        self._symbols = tuple(x for x in args if not x.IsEpsilon)
        self.hash = hash(self._symbols)

    def __len__(self):
        return len(self._symbols)

    def __add__(self, other):
        if isinstance(other, Symbol):
            return Sentence(*(self._symbols + (other,)))

        if isinstance(other, Sentence):
            return Sentence(*(self._symbols + other._symbols))

        raise TypeError(other)

    def __or__(self, other):
        if isinstance(other, Sentence):
            return SentenceList(self, other)

        if isinstance(other, Symbol):
            return SentenceList(self, Sentence(other))

        raise TypeError(other)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return ("%s " * len(self._symbols) % tuple(self._symbols)).strip()

    def __iter__(self):
        return iter(self._symbols)

    def __getitem__(self, index):
        return self._symbols[index]

    def __eq__(self, other):
        return self._symbols == other._symbols

    def __hash__(self):
        return self.hash

    @property
    def IsEpsilon(self):
        return True if len(self._symbols) == 0 else False


class SentenceList(object):
    def __init__(self, *args):
        self._sentences = list(args)

    def Add(self, symbol):
        if not symbol and (symbol is None or not symbol.IsEpsilon):
            raise ValueError(symbol)

        self._sentences.append(symbol)

    def __iter__(self):
        return iter(self._sentences)

    def __or__(self, other):
        if isinstance(other, Sentence):
            self.Add(other)
            return self

        if isinstance(other, Symbol):
            return self | Sentence(other)


class Epsilon(Terminal, Sentence):
    def __init__(self, grammar):
        super().__init__("epsilon", grammar)

    def __str__(self):
        return "e"

    def __repr__(self):
        return "epsilon"

    def __iter__(self):
        yield self

    def __len__(self):
        return 0

    def __add__(self, other):
        return other

    def __eq__(self, other):
        return isinstance(other, (Epsilon,))

    def __hash__(self):
        return hash("")

    @property
    def IsEpsilon(self):
        return True


class Production(object):
    def __init__(self, nonTerminal, sentence):

        self.Left = nonTerminal
        self.Right = sentence

    def __str__(self):

        return "%s := %s" % (self.Left, self.Right)

    def __repr__(self):
        return "%s --> %s" % (
            self.Left,
            self.Right.Grammar.Epsilon if self.IsEpsilon else self.Right,
        )

    def __iter__(self):
        yield self.Left
        yield self.Right

    def __eq__(self, other):
        return (
            isinstance(other, Production) and self.Left == other.Left and self.Right == other.Right
        )

    def __hash__(self):
        return hash((self.Left, self.Right))

    @property
    def IsEpsilon(self):
        return self.Right.IsEpsilon


class AttributeProduction(Production):
    def __init__(self, nonTerminal, sentence, attributes):
        if not isinstance(sentence, Sentence) and isinstance(sentence, Symbol):
            sentence = Sentence(sentence)
        super(AttributeProduction, self).__init__(nonTerminal, sentence)

        self.attributes = attributes

    def __str__(self):
        return "%s := %s" % (self.Left, self.Right)

    def __repr__(self):
        return "%s --> %s" % (self.Left, self.Right)

    def __iter__(self):
        yield self.Left
        yield self.Right

    @property
    def IsEpsilon(self):
        return self.Right.IsEpsilon

    # sintetizar en ingles??????, pending aggrement
    def syntetice(self):
        pass


class Grammar:
    def __init__(self):

        self.Productions = []
        self.nonTerminals = []
        self.terminals = []
        self.startSymbol = None
        # production type
        self.pType = None
        self.Epsilon = Epsilon(self)
        self.EOF = EOF(self)

        self.symbDict = {}

    def NonTerminal(self, name, startSymbol=False):

        name = name.strip()
        if not name:
            raise Exception("Empty name")

        term = NonTerminal(name, self)

        if startSymbol:

            if self.startSymbol is None:
                self.startSymbol = term
            else:
                raise Exception("Cannot define more than one start symbol.")

        self.nonTerminals.append(term)
        self.symbDict[name] = term
        return term

    def NonTerminals(self, names):

        ans = tuple((self.NonTerminal(x) for x in names.strip().split()))

        if len(ans) == 1:
            ans = ans[0]

        return ans

    def Add_Production(self, production):

        if len(self.Productions) == 0:
            self.pType = type(production)

        assert type(production) == self.pType, "The Productions most be of only 1 type."

        production.Left.productions.append(production)
        self.Productions.append(production)

    def Remove_Production(self, production):

        if len(self.Productions) == 0:
            return

        assert type(production) == self.pType, "The Productions most be of only 1 type."

        production.Left.productions.remove(production)
        if production in self.Productions:
            self.Productions.remove(production)

    def Remove_Symbol(self, symbol):
        print("symbol",symbol)
        if symbol != self.Epsilon:
            assert isinstance(symbol, Symbol)
            if self.startSymbol == symbol:
                self.symbDict = {}
                self.startSymbol = None
                self.terminals = []
                self.nonTerminals = []
                self.Productions = []
                return
            if symbol.IsEpsilon:
                return
            to_delete = self.nonTerminals[:] + self.terminals[:]
            for prod in self.Productions[:]:
                if prod.Left == symbol or symbol in prod.Right:
                    self.Remove_Production(prod)
                else:
                    for s in [prod.Left] + list(prod.Right[:]):
                        if s in to_delete:
                            to_delete.remove(s)
            for sym in to_delete:
                if isinstance(sym, Terminal):
                    self.terminals.remove(sym)
                else:
                    self.nonTerminals.remove(sym)
                del self.symbDict[sym.Name]
        return

    def Terminal(self, name):

        name = name.strip()
        if not name:
            raise Exception("Empty name")

        term = Terminal(name, self)
        self.terminals.append(term)
        self.symbDict[name] = term
        return term

    def Terminals(self, names):

        ans = tuple((self.Terminal(x) for x in names.strip().split()))

        if len(ans) == 1:
            ans = ans[0]

        return ans

    def tokenize(self, text):
        try:
            if isinstance(text, str):
                return [self.symbDict[word] for word in text.split()] + [self.EOF]
            if isinstance(text, (list, tuple)):
                return [self.symbDict[word] for word in text] + [self.EOF]
        except KeyError:
            pass
        return [self.EOF]

    def __getitem__(self, symbol_name):
        return self.symbDict[symbol_name]
    
    def __setitem__(self, symbol_name, value):
        assert isinstance(value, Symbol)
        self.symbDict[symbol_name] = value

    def __str__(self):

        mul = "%s, "

        ans = "No Terminales:\n\t"
        if self.nonTerminals:
            nonterminals = mul * (len(self.nonTerminals) - 1) + "%s\n"

            ans += nonterminals % tuple(self.nonTerminals)

        ans += "Terminales:\n\t"
        if self.terminals:

            terminals = mul * (len(self.terminals) - 1) + "%s\n"

            ans += terminals % tuple(self.terminals)

        ans += "Producciones:\n\t"

        ans += "\n\t".join(repr(p) for p in self.Productions) + "\n" if self.Productions else "\n"

        return ans

    @property
    def plain_productions(self):
        return "\n".join(repr(p) for p in self.Productions) if self.Productions else ""

    @property
    def to_json(self):

        productions = []

        for p in self.Productions:
            head = p.Left.Name

            body = []

            for s in p.Right:
                body.append(s.Name)

            productions.append({"Head": head, "Body": body})

        d = {
            "NonTerminals": [symb.Name for symb in self.nonTerminals],
            "Terminals": [symb.Name for symb in self.terminals],
            "Productions": productions,
        }

        # [{'Head':p.Left.Name, "Body": [s.Name for s in p.Right]} for p in self.Productions]
        return json.dumps(d)

    @staticmethod
    def from_json(data):
        data = json.loads(data)

        G = Grammar()
        dic = {"epsilon": G.Epsilon}

        for term in data["Terminals"]:
            dic[term] = G.Terminal(term)

        for noTerm in data["NonTerminals"]:
            dic[noTerm] = G.NonTerminal(noTerm)

        for p in data["Productions"]:
            head = p["Head"]
            dic[head] %= (
                G.Epsilon
                if p["Body"][0] in ("epsilon", "e")
                else Sentence(*[dic[term] for term in p["Body"]])
            )

        return G

    def copy(self):
        G = Grammar()
        G.Productions = self.Productions.copy()
        G.nonTerminals = self.nonTerminals.copy()
        G.terminals = self.terminals.copy()
        G.pType = self.pType
        G.startSymbol = self.startSymbol
        G.Epsilon = self.Epsilon
        G.EOF = self.EOF
        G.symbDict = self.symbDict.copy()

        return G

    @property
    def IsAugmentedGrammar(self):
        return len([0 for left, _ in self.Productions if self.startSymbol == left]) <= 1

    def AugmentedGrammar(self, force=False):
        if not self.IsAugmentedGrammar or force:

            G = self.copy()
            # S, self.startSymbol, SS = self.startSymbol, None, self.NonTerminal('S\'', True)
            S = G.startSymbol
            G.startSymbol = None

            count = 1
            while f"{S.Name}" + count * "'" in self.symbDict:
                count += 1

            SS = G.NonTerminal(f"{S.Name}" + count * "'", True)
            if G.pType is AttributeProduction:
                SS %= S + G.Epsilon, lambda x: x
            else:
                SS %= S + G.Epsilon

            return G
        else:
            return self.copy()

    # endchange
