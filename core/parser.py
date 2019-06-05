from .grammar import Grammar
import fileinput
import re

SYMBOLS_NAME = {
    '+': 'plus',
    '-': 'minus',
    '*': 'star',
    '/': 'slash',
    '\\': 'backslash',
    '{': 'obraket',
    '}': 'cbraket',
    '[': 'osquad',
    ']': 'csquad',
    '(': 'opar',
    ')': 'cpar',
    '^': 'pte',
    '@': 'epsilon',
}
# falta r'[0-9]+': 'num'

def read_from_file(files):
    lines = []
    for line in fileinput.input(files):
        lines.append(line.strip('\n'))
    return lines

def read_from_stdin():
    lines = []
    line = 'some'

    while line != '':
        line = input()
        if line != '':
            lines.append(line)
    return lines

def parse_to_grammar(lines):
    productions = {}
    for line in lines:
        sub_epsilon = re.sub(r'epsilon', '@', line)
        without_spaces = re.sub(r' |\n', '', sub_epsilon)
        head, prods = re.split(r'-->', without_spaces, 1)
    
        try:
            productions[head]
        except KeyError:
            productions[head] = []
        productions[head].extend([e for e in re.split(r'\|', prods) if e != ''])
    non_terminals = [sym for sym in productions]
    terminals = []

    for prod in (p for p_list in productions.values() for p in p_list):
        for ch in prod:
            if ch not in terminals and ch not in non_terminals and get_symbol_name(ch) != "epsilon":
                terminals.append(ch)
    
    G = Grammar()
    script = build_script(terminals, non_terminals, productions)
    # print(script)
    exec(script, {'G': G, '__name__':__name__,}, {})
    
    return G

def get_symbol_name(symbol: str, on_production=False):
    if symbol.isnumeric():
        return "num_{0}".format(symbol)
    if on_production and SYMBOLS_NAME.get(symbol, symbol) == 'epsilon':
        return "G.Epsilon"
    return SYMBOLS_NAME.get(symbol, symbol)

def get_symbols_assignament(terminals, non_terminals):
    # distinguish
    sentence_dist = "{0} = G.NonTerminal('{1}', True)\n".format(non_terminals[0], non_terminals[0])

    # non terminals
    to_assign = ', '.join(map(get_symbol_name, non_terminals[1:])) # except the distiguish (first one)
    arg = ' '.join(non_terminals[1:])
    sentence_nt = "{0} = G.NonTerminals('{1}')\n".format(to_assign, arg)

    # terminals 
    to_assign = ', '.join(map(get_symbol_name, terminals))
    arg = ' '.join(terminals)
    sentence_t = "{0} = G.Terminals('{1}')\n\n".format(to_assign, arg)
    
    return sentence_dist + sentence_nt + sentence_t

def get_attrs(non_terminal, production):# depricated
    return '' # ', None' * (len(production) + (0 if production[0] == '@'  else 1)) #TODO: Faltan los atributos.

def get_production_assignament(non_terminal, productions):
    assigns = "# ===============  {0} --> {1}  ===================== #\n".format(non_terminal, ' | '.join(re.sub(r'@', 'epsilon', string) for string in productions))
    
    for production in productions:
        assigns += "{0} %= {1}".format(get_symbol_name(non_terminal, on_production=True), \
            ' + '.join(get_symbol_name(s, on_production=True) for s in production)) #, lambda h,s: s[2], None, lambda h,s: s[1]"
        assigns += get_attrs(non_terminal, production)
        assigns += '\n'

    assigns += '\n'
    return assigns

def build_script(terminals, non_terminals, productions):
    header = "# Generated Code #\n"
    imports = ""#( "from grammar import Grammar\n") # TODO: cambiar las importaciones

    initiate_symbols = get_symbols_assignament(terminals, non_terminals)

    productions_assign = "############################ BEGIN PRODUCTIONS ############################\n\n"
    for nt in productions:
        productions_assign += get_production_assignament(nt, productions[nt])
    productions_assign += "############################# END PRODUCTIONS #############################\n"
    
    return header + imports + initiate_symbols + productions_assign

# print(parse_to_grammar(read_from_stdin()))

# S --> sS| sdA|dsB
# A --> sd | epsilon
# B --> s
# B --> d | epsilon


