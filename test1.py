from core import *

G = parse_to_grammar(read_from_file("./test_regular.txt"))
# print(G)
# for i in G.Productions:
# 	# if i.Left.Name in ('S', 'S_0', 'A', 'A_1', 'B', 'B_2'): 
# 	print(i)
# print('\n\n')

#remove_left_rec(G)
#lambda_productions(G)
# useless_productions(G)

# print(G)
# for i in G.Productions:
#     # if i.Left.Name in ('S', 'S_0', 'A', 'A_1', 'B', 'B_2'): 
# 	print(i)
# print('\n\n')

# useless_productions(G)

# print(G)
# for i in G.Productions:
#     # if i.Left.Name in ('S', 'S_0', 'A', 'A_1', 'B', 'B_2'): 
# 	print(i)
print(is_regular_grammar(G))
nfa = convert_to_nfa(G)

f = open("./salida.html", "w+")
f.write(nfa._repr_svg_())
f.close()

print(nfa)
print(nfa.regexs)
