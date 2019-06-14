from .parser_tools import compute_firsts, compute_follows


def build_parsing_table(G, firsts, follows):
    # init parsing table
    M = {}

    # P: X -> alpha
    for production in G.Productions:
        X = production.Left
        alpha = production.Right

        ###################################################
        # working with symbols on First(alpha) ...
        ###################################################
        if not production.IsEpsilon:
            for first in firsts[alpha]:
                M[X, first] = [production]
        ###################################################

        ###################################################
        # working with epsilon...
        ###################################################
        else:
            for follow in follows[X]:
                M[X, follow] = [production]
        ###################################################

    # parsing table is ready!!!
    return M


def metodo_predictivo_no_recursivo(G, M=None, firsts=None, follows=None):

    # checking table...
    if M is None:
        if firsts is None:
            firsts = compute_firsts(G)
        if follows is None:
            follows = compute_follows(G, firsts)
        M = build_parsing_table(G, firsts, follows)

    # parser construction...
    def parser(w):

        ###################################################
        # w ends with $ (G.EOF)
        ###################################################
        # init:
        stack = [G.startSymbol]
        cursor = 0
        output = []
        ###################################################

        # parsing w...
        while True:
            top = stack.pop()
            a = w[cursor]

            #             print((top, a))

            ###################################################
            if top.IsTerminal:
                if a == top:
                    cursor += 1
                else:
                    raise ("parsing error")

            elif top.IsNonTerminal:
                production = M[top, a][0]

                if production != None:
                    alpha = production.Right
                    output.append(production)
                    for i in range(len(alpha)):
                        stack.append(alpha[-i - 1])

                else:
                    raise ("parsing error")

            if len(stack) == 0:
                break
        # output = stack.count == 0 and cursor == len(w)
        ###################################################

        # left parse is ready!!!
        return output

    # parser is ready!!!
    return parser

