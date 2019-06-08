from itertools import islice, compress, product
from .grammar import NonTerminal, Grammar, Sentence, SentenceList


class ContainerSet:
    def __init__(self, *values, contains_epsilon=False):
        self.set = set(values)
        self.contains_epsilon = contains_epsilon

    def add(self, value):
        n = len(self.set)
        self.set.add(value)
        return n != len(self.set)

    def set_epsilon(self, value=True):
        last = self.contains_epsilon
        self.contains_epsilon = value
        return last != self.contains_epsilon

    def update(self, other):
        n = len(self.set)
        self.set.update(other.set)
        return n != len(self.set)

    def epsilon_update(self, other):
        return self.set_epsilon(self.contains_epsilon | other.contains_epsilon)

    def hard_update(self, other):
        return self.update(other) | self.epsilon_update(other)

    def __len__(self):
        return len(self.set) + int(self.contains_epsilon)

    def __str__(self):
        return "%s-%s" % (str(self.set), self.contains_epsilon)

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return iter(self.set)

    def __eq__(self, other):
        return (
            isinstance(other, ContainerSet)
            and self.set == other.set
            and self.contains_epsilon == other.contains_epsilon
        )


# Computes First(alpha), given First(Vt) and First(Vn)
# alpha in (Vt U Vn)*
def compute_local_first(firsts, alpha):
    first_alpha = ContainerSet()

    try:
        alpha_is_epsilon = alpha.IsEpsilon
    except:
        alpha_is_epsilon = False

    ###################################################
    # alpha == epsilon ? First(alpha) = { epsilon }
    ###################################################
    if alpha_is_epsilon:
        first_alpha.set_epsilon()
    ###################################################

    ###################################################
    # alpha = X1 ... XN
    # First(Xi) subconjunto First(alpha)
    # epsilon pertenece a First(X1)...First(Xi) ? First(Xi+1) subconjunto de First(X) y First(alpha)
    # epsilon pertenece a First(X1)...First(XN) ? epsilon pertence a First(X) y al First(alpha)
    ###################################################
    else:
        for symbol in alpha:
            first_alpha.update(firsts[symbol])
            if not firsts[symbol].contains_epsilon:
                break
        else:
            first_alpha.set_epsilon()
    ###################################################

    # First(alpha)
    return first_alpha


# Computes First(Vt) U First(Vn) U First(alpha)
# P: X -> alpha
def compute_firsts(G):
    firsts = {}
    change = True

    # init First(Vt)
    for terminal in G.terminals:
        firsts[terminal] = ContainerSet(terminal)

    # init First(Vn)
    for nonterminal in G.nonTerminals:
        firsts[nonterminal] = ContainerSet()

    while change:
        change = False

        # P: X -> alpha
        for production in G.Productions:
            X = production.Left
            alpha = production.Right

            # get current First(X)
            first_X = firsts[X]

            # init First(alpha)
            try:
                first_alpha = firsts[alpha]
            except:
                first_alpha = firsts[alpha] = ContainerSet()

            # CurrentFirst(alpha)???
            local_first = compute_local_first(firsts, alpha)

            # update First(X) and First(alpha) from CurrentFirst(alpha)
            change |= first_alpha.hard_update(local_first)
            change |= first_X.hard_update(local_first)

    # First(Vt) + First(Vt) + First(RightSides)
    return firsts


def compute_follows(G, firsts):
    follows = {}
    change = True

    # local_firsts = {}

    # init Follow(Vn)
    for nonterminal in G.nonTerminals:
        follows[nonterminal] = ContainerSet()
    follows[G.startSymbol] = ContainerSet(G.EOF)

    while change:
        change = False

        # P: X -> alpha
        for production in G.Productions:
            X = production.Left
            alpha = production.Right

            follow_X = follows[X]

            ###################################################
            # X -> zeta Y beta
            # First(beta) - { epsilon } subset of Follow(Y)
            # beta ->* epsilon or X -> zeta Y ? Follow(X) subset of Follow(Y)
            ###################################################
            for i, item in enumerate(alpha):
                if item.IsTerminal:
                    continue
                Y = alpha[i]
                first_beta = compute_local_first(firsts, alpha[(i + 1) :])
                change |= follows[Y].update(first_beta)
                if first_beta.contains_epsilon or i == len(alpha) - 1:
                    change |= follows[Y].update(follow_X)
            ###################################################

    # Follow(Vn)
    return follows


def get_new_nonterminal(nt_father, suffix, G):
    return NonTerminal("{0}'".format(nt_father), G)


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
    queue = [G.startSymbol]
    # productions_to_delete = [G.Productions[:]]
    while queue:
        cur_nt = queue.pop()
        for p in cur_nt.productions:
            # productions_to_delete.remove(p)
            for sym in p.Right:
                if sym.IsNonTerminal and sym not in visited:
                    queue.insert(0, sym)
                    visited.append(sym)
    for nt in G.nonTerminals:
        if nt not in visited:
            G.Remove_Symbol(nt)
    return G


def set_all_combinations(production, nulleables):
    gen_combs = combinations([nt for nt in production.Right if nt in nulleables])

    for comb in gen_combs:
        body = list(production.Right[:])
        modified = False
        for _nt in comb:
            if _nt in body:
                modified = True
                body.remove(_nt)
        if modified and body:
            production.Left %= Sentence(*body)
    return


def combinations(items):
    return (set(compress(items, mask)) for mask in product(*[[0, 1]] * len(items)))


def lambda_productions(G: Grammar):
    nulleables = [
        nt for nt in G.nonTerminals if any(prod.Right.IsEpsilon for prod in nt.productions)
    ]

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
            set_all_combinations(p, nulleables)

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


def Remove_Useless_Productions(Grammar):
    visited = []
    Incomming = []
    bads = []

    print("producciones", Grammar.Productions)

    initial = Grammar.startSymbol

    Incomming.append(initial)

    while len(Incomming) > 0:
        t = Incomming.pop()
        if not t in visited:
            visited.append(t)
            for prod in Grammar.Productions:
                if prod.Left == t:
                    for i in prod.Right:
                        if i.IsNonTerminal and i not in visited and i not in Incomming:
                            Incomming.append(i)

    for i in Grammar.nonTerminals:
        if i not in visited:
            bads.append(i)

    print("bads", bads)

    # construir la gramatica


def Remove_Bads_Productions(Grammar):
    dicc = {}

    for t in Grammar.terminals:
        dicc[t] = True

    for nt in Grammar.nonTerminals:
        dicc[nt] = False

    # dicc['epsilon'] = True
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

    print(dicc)
