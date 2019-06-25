from pandas import DataFrame
from grammar import Terminal
import prettytable as ptable

try:
    import pydot
except:
    pass

SHIFT = "shift"
REDUCE = "reduce"
OK = "ok"
ERROR = "error"

GOTO = "goto"
ACTION = "action"
OTHER = "other"


class DerivationTree:
    def __init__(self, symbol):
        self.symbol = symbol
        self.children = []

    def add_child(self, child_tree):
        self.children.append(child_tree)

    @staticmethod
    def get_tree_at(parser, index, parser_type="left"):
        production = parser[index]
        tree = DerivationTree(production.Left)
        end = index + 1

        sentence = reversed(production.Right) if parser_type == "right" else production.Right

        for symbol in sentence:
            if symbol.IsTerminal:
                tree.add_child(DerivationTree(symbol))
            else:
                ctree, end = DerivationTree.get_tree_at(parser, end, parser_type)
                tree.add_child(ctree)

        if parser_type == "right":
            tree.children.reverse()

        return tree, end

    @staticmethod
    def get_tree(parser, parser_type="left"):
        return DerivationTree.get_tree_at(parser, 0, parser_type)[0]

    def graph(self):
        # G = pydot.Dot(rankdir='LR', margin=0.1)
        G = pydot.Dot(rankdir="TD", margin=0.1)
        G.add_node(pydot.Node("start", shape="plaintext", label="", width=0, height=0))

        visited = set()

        def visit(start):
            ids = id(start)
            if ids not in visited:
                visited.add(ids)
                G.add_node(
                    pydot.Node(
                        ids,
                        label=start.symbol.Name,
                        shape="circle",
                        style="bold" if isinstance(start.symbol, Terminal) else "",
                    )
                )
                for tree in start.children:
                    visit(tree)
                    G.add_edge(pydot.Edge(ids, id(tree), labeldistance=2))

        visit(self)
        G.add_edge(pydot.Edge("start", id(self), label="", style="dashed"))

        return G

    def _repr_svg_(self):
        try:
            return self.graph().create_svg().decode("utf8")
        except Exception as err:
            print(err.__traceback__, err)
            pass

    def __str__(self):
        return self.symbol.Name + "[" + "][".join(str(child) for child in self.children) + "]"


def multiline_formatter(state):
    return "\n".join(str(item) for item in state)


def conflict_cond_ll1(cell: list):
    return isinstance(cell, list) and len(cell) > 1


def empty_formatter(state):
    return ""


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

