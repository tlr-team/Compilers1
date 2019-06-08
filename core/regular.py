from core.grammar import Grammar
from core.parser_tools import lambda_productions
from core.automaton import NFA

def convert_to_nfa(G: Grammar):
    #g = lambda_productions(G)
    #print("antes",g)
    #g = G

    n = len(g.nonTerminals) + 1
    states = n
    finals = [n]
    transitions = {}

    dicc = { p:i for i,p in enumerate(g.nonTerminals) }

    print(g.Productions)

    for p in g.Productions:
        if(len(p.Right) > 1):
            transitions[(dicc[p.Left],p.Right[0])] = [dicc[p.Right[1]]]
        else:
            transitions[(dicc[p.Left],p.Right[0])] = [n]
        
        if p.Left == g.startSymbol and p.Right.IsEpsilon:
            finals.append(dicc[p.Left])
    
    sol = NFA(states, finals, transitions)

    return sol

