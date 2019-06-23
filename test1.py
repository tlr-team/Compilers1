from parse_input import *
from parsers import *
from regex import *

test_name = "reg1"
G = parse_to_grammar(read_from_file(f"./examples/test_{test_name}.txt"))
# print(G)
# for i in G.Productions:
# 	# if i.Left.Name in ('S', 'S_0', 'A', 'A_1', 'B', 'B_2'):
# 	print(i)
# print('\n\n')

# remove_left_rec(G)
# lambda_productions(G)
# useless_productions(G)


print(is_regular_grammar(G))
nfa = convert_to_nfa(G)

print(nfa._repr_svg_())
# f = open("./salida.html", "w+")
# f.write(nfa._repr_svg_())
# f.close()

# print(nfa)
# print(nfa.regexs)
# print(regex_state_remove(nfa.regexs,1))
# print(regex_from_nfa(nfa))

firsts= compute_firsts(G)
follows = compute_follows(G, firsts)

# print(remove_unit_productions(G))
# print(remove_left_rec(G))
ll1 = LL1(G,firsts=firsts,follows=follows)
# lr1 = LR1(G)
print(ll1)
print(ll1("az")[1])
# print(lr1)

