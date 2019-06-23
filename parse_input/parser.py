from grammar import Grammar
import fileinput
import re

SYMBOLS_NAME = {
    "+": "plus",
    "-": "minus",
    "*": "star",
    "/": "slash",
    "\\": "backslash",
    "{": "obraket",
    "}": "cbraket",
    "[": "osquad",
    "]": "csquad",
    "(": "opar",
    ")": "cpar",
    "^": "pte",
    ".": "dot",
    ",": "comma",
    ":": "dotdot",  # jeje no me acordaba
    ";": "semicolon",
    "e": "epsilon",
    "epsilon": "epsilon",
}
# falta r'[0-9]+': 'num'


def read_from_file(files):
    lines = []
    for line in fileinput.input(files):
        lines.append(line.strip("\n"))
    return lines


def read_from_stdin():
    lines = []
    line = "some"

    while line != "":
        line = input()
        if line != "":
            lines.append(line)
    return lines


def parse_to_grammar(lines):
    productions = {}
    non_terminals = []
    terminals = []
    try:
        for line in lines:
            if line.strip() in ("\n", ""):
                continue

            sub_epsilon = re.sub(r"epsilon", "e", line)
            without_endline = re.sub(r"\n", "", sub_epsilon).strip()
            without_spaces = re.sub(r"\| | \| | \|", "|", without_endline)
            head, prods = [i.strip() for i in re.split(r"-->", without_spaces, 1)]

            head = head.strip()
            assert all( c not in head for c in " -\t"), "bad format"
            prods = prods.strip()

            if head not in non_terminals:
                non_terminals.append(head)

            cur_prods = []
            for prod in re.split(r"\|", prods):
                if prod != "":
                    pass
                cur_prods.append([symbol for symbol in re.split(r" ", prod) if symbol != ""])

            try:
                productions[head]
            except KeyError:
                productions[head] = []
            productions[head].extend(cur_prods)

        prods = (prod for p_list in productions.values() for prod in p_list)
        for prod in prods:
            for sym in prod:
                if (
                    sym not in terminals
                    and sym not in non_terminals
                    and get_symbol_name(sym) != "epsilon"
                ):
                    terminals.append(sym)

        G = Grammar()
        script = build_script(terminals, non_terminals, productions)
        print(script)
        exec(script, {"G": G, "__name__": __name__}, {})
        return G
    except:
        return None


def get_symbol_name(symbol: str, on_production=False):
    if symbol == "G":
        return "_G"
    elif SYMBOLS_NAME.get(symbol, symbol) == "epsilon":
        return "G.Epsilon" if on_production else SYMBOLS_NAME.get(symbol, symbol)
    elif symbol.isalpha():
        return symbol
    elif symbol.isnumeric():
        return "num_{0}".format(symbol)
    elif len(symbol) == 1:
        return SYMBOLS_NAME.get(symbol, symbol)

    name = "" if symbol[0].isalpha() else "_"
    for c in symbol:
        name += SYMBOLS_NAME.get(c, c)
    return name


def get_symbols_assignament(terminals, non_terminals):
    # distinguish
    sentence_dist = (
        ""
        if not non_terminals
        else "{0} = G.NonTerminal('{1}', True)\n".format(non_terminals[0], non_terminals[0])
    )

    # non terminals
    to_assign = ", ".join(map(get_symbol_name, non_terminals[1:]))
    # except the distiguish (first one)
    arg = " ".join(non_terminals[1:])
    sentence_nt = (
        "" if not non_terminals[1:] else "{0} = G.NonTerminals('{1}')\n".format(to_assign, arg)
    )

    # terminals
    to_assign = ", ".join(map(get_symbol_name, terminals))
    arg = " ".join(terminals)
    sentence_t = "" if not terminals else "{0} = G.Terminals('{1}')\n\n".format(to_assign, arg)

    return sentence_dist + sentence_nt + sentence_t


def get_attrs(non_terminal, production):  # depricated
    return (
        ""
    )  # ', None' * (len(production) + (0 if production[0] == 'e'  else 1)) #TODO: Faltan los atributos.


def get_production_assignament(non_terminal, productions):
    prods_formatted = []
    prods_to_operate = []
    for prod in productions:
        prods_formatted.append(" ".join(sym for sym in prod))
        prods_to_operate.append(
            " + ".join(get_symbol_name(sym, on_production=True) for sym in prod)
        )
    assigns = "# ===============  {{ {0} --> {1} }}  ===================== #\n".format(
        non_terminal, " | ".join(re.sub(r"e", "epsilon", p) for p in prods_formatted)
    )

    for production in prods_to_operate:
        assigns += "{0} %= {1}".format(
            get_symbol_name(non_terminal, on_production=True), production
        )
        assigns += get_attrs(non_terminal, production)
        assigns += "\n"

    assigns += "\n"
    return assigns


def build_script(terminals, non_terminals, productions):
    header = "# Generated Code #\n"
    imports = ""  # ( "from grammar import Grammar\n") # TODO: cambiar las importaciones

    initiate_symbols = get_symbols_assignament(terminals, non_terminals)

    productions_assign = (
        "############################ BEGIN PRODUCTIONS ############################\n\n"
    )
    for nt in productions:
        productions_assign += get_production_assignament(nt, productions[nt])
    productions_assign += (
        "############################# END PRODUCTIONS #############################\n"
    )

    return header + imports + initiate_symbols + productions_assign


# print(parse_to_grammar(read_from_stdin()))

# S --> sS| sdA|dsB
# A --> sd | epsilon
# B --> s
# B --> d | epsilon

