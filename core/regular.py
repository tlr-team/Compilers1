from core.grammar import Grammar
from core.parser_tools import lambda_productions,useless_productions
from core.automaton import NFA

def convert_to_nfa(G: Grammar):
    t = lambda_productions(G)
    g = useless_productions(t)
    print("despues",g)
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

def regex_state_remove(regex: dict, state: int):
    predecesores = {}
    sucesores = {}
    ciclo = ""
    for (a,b) in regexs.keys():
        if a == state and b != state:
            sucesores[b] = N.regexs[(a,b)]
        elif b == state and a != state:
            predecesores[a] = N.regexs[(a,b)]
        elif a == b == state:
            ciclo = N.regexs[(a,b)]

    ciclo = ciclo + "*" if ciclo != "" else ""

    for pred in predecesores.keys():
        for suc in sucesores.keys():
            try:
                N.regexs[(pred,suc)] +=  "|" + "( " + predecesores[pred] + ciclo + sucesores[suc] + " )"
            except KeyError:
                N.regexs[(pred,suc)] = predecesores[pred] + ciclo + sucesores[suc]

    news = {}
    for (a,b) in N.regexs.keys():
        if a != state and b != state:
            d = a if a < state else a-1
            e = b if b < state else b-1
            news[(d,e)] = N.regexs[(a,b)]

    return news
