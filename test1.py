from core import *

G = parse_to_grammar(read_from_file("./test.txt"))
for i in G.Productions:
    if i.Left.Name in ('S', 'S_0', 'A', 'A_1', 'B', 'B_2'): 
        print(i)
print()
remove_left_rec(G)
for i in G.Productions:
    if i.Left.Name in ('S', 'S_0', 'A', 'A_1', 'B', 'B_2'): 
        print(i)
