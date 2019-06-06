from itertools import islice
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
    return NonTerminal("{0}_{1}".format(nt_father, suffix), G)

def production_begin_ntj(nt_ordered, curr_i, body):
    return not body.IsEpsilon and body[0] in nt_ordered[:curr_i]


def take_of_initial(body, G):
    if len(body) == 1:
        return (body[0], Sentence(G.Epsilon))
    return (body[0], Sentence(*body[1:]))


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
    nts_ordered = G.nonTerminals
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
