from .grammar import Grammar
from .parser_tools import lambda_productions,useless_productions
from .automaton import NFA

def convert_to_nfa(G: Grammar):
    t = lambda_productions(G)
    g = useless_productions(t)
    #print("antes",g)
    #g = G

    n = len(g.nonTerminals) + 1
    states = n
    finals = [n]
    transitions = {}

    dicc = { p:i for i,p in enumerate(g.nonTerminals) }

    print(g.Productions)

    for p in g.Productions:
        try:
            if len(p.Right) > 1:
                transitions[(dicc[p.Left],p.Right[0])].append(dicc[p.Right[1]])
            else:
                transitions[(dicc[p.Left],p.Right[0])].append(n)

        except KeyError:
            if len(p.Right) > 1:
                transitions[(dicc[p.Left],p.Right[0])] = [dicc[p.Right[1]]]
            else:
                transitions[(dicc[p.Left],p.Right[0])] = [n]
            

        if p.Left == g.startSymbol and p.Right.IsEpsilon:
            finals.append(dicc[p.Left])
    sol = NFA(states, finals, transitions)

    return sol

