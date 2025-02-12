from itertools import islice, compress, product
from grammar import NonTerminal, Grammar, Sentence, SentenceList, Production
from copy import deepcopy


def get_new_nonterminal(nt_father, suffix, G):
    return G.NonTerminal("{0}'".format(nt_father))


def production_begin_ntj(nt_ordered, curr_i, body):
    return not body.IsEpsilon and body[0] in nt_ordered[:curr_i]


def take_of_initial(body, G):
    if len(body) == 1:
        return (body[0], Sentence(G.Epsilon))
    return (body[0], Sentence(*body[1:]))


def get_topological_order(G: Grammar):
    ordered = [G.startSymbol]
    queue = [G.startSymbol]
    while queue:
        cur_nt = queue.pop()
        for p in cur_nt.productions:
            for sym in p.Right:
                if sym.IsNonTerminal and sym not in ordered:
                    queue.insert(0, sym)
                    ordered.append(sym)
    return ordered


def remove_direct_left_rec_on(nt: NonTerminal, curr_suff):
    G = nt.Grammar
    bad_prods, others = [], []
    for prod in nt.productions:
        if not prod.Right.IsEpsilon and prod.Left == prod.Right[0]:
            bad_prods.append(prod)
        else:
            others.append(prod)
    new_nt = None
    if bad_prods:
        new_nt = get_new_nonterminal(prod.Left, curr_suff, G)
        for prod in bad_prods:
            _, alfa = take_of_initial(prod.Right, G)
            new_nt %= alfa + new_nt
            G.Remove_Production(prod)
        new_nt %= G.Epsilon

        for prod in others:
            nt %= prod.Right + new_nt
            G.Remove_Production(prod)

        curr_suff += 1
    return curr_suff, new_nt


def remove_direct_left_rec(G: Grammar):
    suff_nt = {nt: 0 for nt in G.nonTerminals}

    for nt in G.nonTerminals:
        suff_nt[nt], new_nt = remove_direct_left_rec_on(nt, suff_nt[nt])
        if new_nt:
            suff_nt[new_nt] = 0


def remove_left_rec(G: Grammar):
    non_terminals = G.nonTerminals

    ### del( S --> S ) ###
    for nt in non_terminals:
        for p in nt.productions[:]:
            if len(p.Right) == 1 and p.Right[0].Name == nt.Name:
                G.Remove_Production(p)

    ### Topological Order ###
    nts_ordered = get_topological_order(G)
    suff = 0
    for i in range(len(nts_ordered)):
        Ai: NonTerminal = nts_ordered[i]
        changes = True
        while changes:
            changes = False
            for pi in Ai.productions[:]:
                ai = pi.Right
                if production_begin_ntj(nts_ordered, i, ai):
                    changes = True
                    Aj, bi = take_of_initial(ai, G)
                    G.Remove_Production(pi)
                    for pj in Aj.productions:
                        Ai %= pj.Right + bi

        ### Direct Left Recursion ##
        remove_direct_left_rec_on(Ai, suff)
        suff += 1
    return G


def useless_productions(G: Grammar):
    visited = [G.startSymbol]
    finalize = [*G.terminals]
    stack = [G.startSymbol]

    while stack:
        cur_nt = stack.pop()
        if cur_nt.IsTerminal:
            continue

        for p in G.Productions:
            if cur_nt == p.Left:
                for symb in p.Right:
                    if symb not in visited:
                        stack.append(symb)
                        visited.append(symb)

    print(visited)

        # for p in cur_nt.productions:
        #     for sym in p.Right:
        #         if sym not in visited:
        #             stack.append(sym)
        #             visited.append(sym)

    toremove = []

    for nt in G.nonTerminals[:]:
        if nt not in visited and nt not in toremove:
            toremove.append(nt)
    
    for nt in toremove:
        G.Remove_Symbol(nt)

    # changes = True
    # while changes:
    #     changes = False
    #     for nt in G.nonTerminals:
    #         if (
    #             any(all(s in finalize for s in prod.Right) for prod in nt.productions)
    #             and nt not in finalize
    #         ):
    #             changes = True
    #             finalize.append(nt)

    # for nt in G.nonTerminals:
    #     if nt not in finalize and nt:
    #         G.Remove_Symbol(nt)
    
    # print("grammar", G)
    return G


def set_all_combinations(production, nulleables):
    gen_combs = combinations([nt for nt in production.Right if nt in nulleables])
    to_add = []

    for comb in gen_combs:
        body = list(production.Right[:])
        modified = False
        for _nt in comb:
            if _nt in body:
                modified = True
                body.remove(_nt)
        if modified and body:
            to_add.append((production.Left.Name, Sentence(*body)))
            # G[production.Left.Name] %= Sentence(*body)
    return to_add


def combinations(items):
    return (set(compress(items, mask)) for mask in product(*[[0, 1]] * len(items)))


def lambda_productions(G: Grammar):
    nulleables = [
        nt for nt in G.nonTerminals if any(prod.Right.IsEpsilon for prod in nt.productions)
    ]
    to_add = []

    changes = True
    while changes:
        changes = False
        for nt in G.nonTerminals:
            if (
                any(
                    prod.Right.IsEpsilon or all(sym in nulleables for sym in prod.Right)
                    for prod in nt.productions
                )
                and nt not in nulleables
            ):
                changes = True
                nulleables.append(nt)

    for p in G.Productions[:]:
        if any(s in nulleables for s in p.Right):
            to_add.extend(set_all_combinations(p, nulleables))

    for l, r in to_add:
        G[l] %= r

    for p in G.Productions:
        if p.Right.IsEpsilon:
            G.Remove_Production(p)
    return G


def is_regular_grammar(G: Grammar):
    answer = True

    for prod in G.Productions:
        if len(prod.Right) > 2:
            answer = False
            break

        if not prod.Right.IsEpsilon:
            if prod.Right[0].IsNonTerminal:
                answer = False
                break
            if len(prod.Right) > 1 and prod.Right[1].IsTerminal:
                answer = False
                break
    return answer


def remove_bads_productions(Grammar):
    dicc = {}

    for t in Grammar.terminals:
        dicc[t] = True

    for nt in Grammar.nonTerminals:
        dicc[nt] = False

    dicc[Grammar.Epsilon] = True
    # dicc['e'] = True

    changed = True

    print(dicc)

    while changed:
        changed = False
        for prod in Grammar.Productions:
            for i in prod.Right:
                print(i)
                if dicc[i] == False:
                    break
            else:
                if dicc[prod.Left] == False:
                    dicc[prod.Left] = True
                    changed = True

    for key in dicc.keys():
        if dicc[key] == False:
            for symb in Grammar.nonTerminals:
                if symb.Name == key:
                    Grammar.Remove_Symbol(symb)

    print(dicc)


def unit_productions(G: Grammar):
    unit_prodution_free = []
    unit_productions = []

    for prod in G.Productions:
        if len(prod.Right) == 1 and prod.Right[0].IsNonTerminal:
            unit_productions.append(prod)
        else:
            unit_prodution_free.append(prod)

    for up in unit_productions:
        right = up.Right[0]
        for nup in unit_prodution_free:
            if nup.Left == right:
                nprod = Production(up.Left, nup.Right)
                for p in unit_prodution_free:
                    if p == nprod:
                        break
                else:
                    unit_prodution_free.append(nprod)

    G.Productions = unit_prodution_free
    return G

