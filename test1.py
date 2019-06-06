from core import *

G = parse_to_grammar(read_from_file("./test.txt"))
print(G)
for i in G.Productions:
	# if i.Left.Name in ('S', 'S_0', 'A', 'A_1', 'B', 'B_2'): 
	print(i)
print('\n\n')
remove_left_rec(G)
useless_productions(G)
print(G)
for i in G.Productions:
    # if i.Left.Name in ('S', 'S_0', 'A', 'A_1', 'B', 'B_2'): 
	print(i)