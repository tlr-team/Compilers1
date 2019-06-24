from parse_input import *
from parsers import *
from regex import *
from grammar import Grammar
from copy import deepcopy
from tools import table_to_dataframe

test_name = "reg1"
G = parse_to_grammar(read_from_file(f"./examples/test_{test_name}.txt"))

# G = Grammar()
# E = G.NonTerminal("E", True)
# A = G.NonTerminal("A")
# equal, plus, num = G.Terminals("= + int")

# E %= A + equal + A | num
# A %= num + plus + A | num


# remove_left_rec(G)
# lambda_productions(G)
# useless_productions(G)


# print(is_regular_grammar(G))
# nfa = convert_to_nfa(G)

# print(nfa._repr_svg_())
# f = open("./salida.html", "w+")
# f.write(nfa._repr_svg_())
# f.close()

# print(nfa)
# print(nfa.regexs)
# print(regex_state_remove(nfa.regexs,1))
# print(regex_from_nfa(nfa))

# firsts = compute_firsts(G)
# follows = compute_follows(G, firsts)

# print(remove_unit_productions(G))
# print(remove_left_rec(G))
ll1 = LL1(deepcopy(G))  # firsts=firsts, follows=follows)
lr1 = LR1(G)
slr = SLR(G)

print(ll1)
print(ll1(["a", "z"])[1])

print(lr1)
print(lr1(["int", "+", "int", "=", G.EOF.Name], verbose=True))

# print(slr)
# print(slr(["int", "+", "int", "=", "int", G.EOF.Name], verbose=True)[1])

