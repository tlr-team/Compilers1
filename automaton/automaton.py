import pydot
from parse_input import lambda_productions
from grammar import Grammar, ContainerSet


class NFA:
    def __init__(self, states, finals, transitions, start=0):
        self.states = states
        self.start = start
        self.finals = set(finals)
        self.map = transitions
        self.vocabulary = set()
        self.transitions = {state: {} for state in range(states)}
        self.regexs = {}

        for (origin, symbol), destinations in transitions.items():
            assert hasattr(destinations, "__iter__"), "Invalid collection of states"
            self.transitions[origin][symbol] = destinations
            self.vocabulary.add(symbol)

        self.vocabulary.discard("")

        for org in self.transitions:
            for symb in self.transitions[org]:
                for dest in self.transitions[org][symb]:
                    try:
                        self.regexs[(org, dest)] += " | " + str(symb)
                    except KeyError:
                        self.regexs[(org, dest)] = str(symb)

        for key in self.regexs.keys():
            if len(self.regexs[key]) > 1:
                self.regexs[key] = "( " + self.regexs[key] + " )"

    def epsilon_transitions(self, state):
        assert state in self.transitions, "Invalid state"
        try:
            return self.transitions[state][""]
        except KeyError:
            return ()

    def graph(self):
        G = pydot.Dot(rankdir="LR", margin=0.1)
        G.add_node(pydot.Node("start", shape="plaintext", label="", width=0, height=0))

        for (start, tran), destinations in self.map.items():
            tran = "ε" if tran == "" else tran
            G.add_node(
                pydot.Node(start, shape="circle", style="bold" if start in self.finals else "")
            )
            for end in destinations:
                G.add_node(
                    pydot.Node(end, shape="circle", style="bold" if end in self.finals else "")
                )
                G.add_edge(pydot.Edge(start, end, label=tran, labeldistance=2))

        G.add_edge(pydot.Edge("start", self.start, label="", style="dashed"))
        return G

    def _repr_svg_(self):
        try:
            return self.graph().create_svg().decode("utf8")
        except:
            pass


class DFA(NFA):
    def __init__(self, states, finals, transitions, start=0):
        assert all(isinstance(value, int) for value in transitions.values())
        assert all(len(symbol) > 0 for origin, symbol in transitions)

        transitions = {key: [value] for key, value in transitions.items()}
        NFA.__init__(self, states, finals, transitions, start)
        self.current = start

    def epsilon_transitions(self):
        raise TypeError()

    def _move(self, symbol):
        try:
            self.current = self.transitions[self.current][symbol][0]
            return True
        except:
            return False
        # Your code here
        # pass

    def _reset(self):
        self.current = self.start

    def recognize(self, string):
        self._reset()
        for symbol in string:
            if not self._move(symbol):
                return False
        return self.current in self.finals
        # Your code here
        pass


class State:
    def __init__(self, state, final=False, formatter=lambda x: str(x)):
        self.state = state
        self.final = final
        self.transitions = {}
        self.epsilon_transitions = set()
        self.tag = None
        self.formatter = formatter

    def set_formatter(self, formatter, visited=None):
        if visited is None:
            visited = set()
        elif self in visited:
            return

        visited.add(self)
        self.formatter = formatter
        for destinations in self.transitions.values():
            for node in destinations:
                node.set_formatter(formatter, visited)
        for node in self.epsilon_transitions:
            node.set_formatter(formatter, visited)
        return self

    def has_transition(self, symbol):
        return symbol in self.transitions

    def add_transition(self, symbol, state):
        try:
            self.transitions[symbol].append(state)
        except:
            self.transitions[symbol] = [state]
        return self

    def add_epsilon_transition(self, state):
        self.epsilon_transitions.add(state)
        return self

    def recognize(self, string):
        states = self.epsilon_closure
        for symbol in string:
            states = self.move_by_state(symbol, *states)
            states = self.epsilon_closure_by_state(*states)
        return any(s.final for s in states)

    def to_deterministic(self, formatter=lambda x: str(x)):
        closure = self.epsilon_closure
        start = State(tuple(closure), any(s.final for s in closure), formatter)

        closures = [closure]
        states = [start]
        pending = [start]

        while pending:
            state = pending.pop()
            symbols = {symbol for s in state.state for symbol in s.transitions}

            for symbol in symbols:
                move = self.move_by_state(symbol, *state.state)
                closure = self.epsilon_closure_by_state(*move)

                if closure not in closures:
                    new_state = State(tuple(closure), any(s.final for s in closure), formatter)
                    closures.append(closure)
                    states.append(new_state)
                    pending.append(new_state)
                else:
                    index = closures.index(closure)
                    new_state = states[index]

                state.add_transition(symbol, new_state)

        return start

    @staticmethod
    def from_nfa(nfa, get_states=False):
        states = []
        for n in range(nfa.states):
            state = State(n, n in nfa.finals)
            state.idx = n
            states.append(state)

        for (origin, symbol), destinations in nfa.map.items():
            origin = states[origin]
            origin[symbol] = [states[d] for d in destinations]

        if get_states:
            return states[nfa.start], states
        return states[nfa.start]

    @staticmethod
    def move_by_state(symbol, *states):
        return {s for state in states if state.has_transition(symbol) for s in state[symbol]}

    @staticmethod
    def epsilon_closure_by_state(*states):
        closure = {state for state in states}

        length = 0
        while length != len(closure):
            length = len(closure)
            tmp = [s for s in closure]
            for s in tmp:
                for epsilon_state in s.epsilon_transitions:
                    closure.add(epsilon_state)
        return closure

    @property
    def epsilon_closure(self):
        return self.epsilon_closure_by_state(self)

    @property
    def name(self):
        return (
            f"{self.tag}\n{self.formatter(self.state)}" if self.tag else self.formatter(self.state)
        )

    def get(self, symbol):
        target = self.transitions[symbol]
        assert len(target) == 1
        return target[0]

    def __getitem__(self, symbol):
        if symbol == "":
            return self.epsilon_transitions
        try:
            return self.transitions[symbol]
        except KeyError:
            return None

    def __setitem__(self, symbol, value):
        if symbol == "":
            self.epsilon_transitions = value
        else:
            self.transitions[symbol] = value

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.state)

    def __hash__(self):
        return hash(self.state)

    def __iter__(self):
        yield from self._visit()

    def _visit(self, visited=None):
        if visited is None:
            visited = set()
        elif self in visited:
            return

        visited.add(self)
        yield self

        for destinations in self.transitions.values():
            for node in destinations:
                yield from node._visit(visited)
        for node in self.epsilon_transitions:
            yield from node._visit(visited)

    def graph(self):
        G = pydot.Dot(rankdir="LR", margin=0.1)
        G.add_node(pydot.Node("start", shape="plaintext", label="", width=0, height=0))

        visited = set()

        def visit(start):
            ids = id(start)
            if ids not in visited:
                visited.add(ids)
                G.add_node(
                    pydot.Node(
                        ids,
                        label=str(start.idx),
                        shape="circle",
                        style="bold" if start.final else "",
                    )
                )
                for tran, destinations in start.transitions.items():
                    for end in destinations:
                        visit(end)
                        G.add_edge(pydot.Edge(ids, id(end), label=tran, labeldistance=2))
                for end in start.epsilon_transitions:
                    visit(end)
                    G.add_edge(pydot.Edge(ids, id(end), label="ε", labeldistance=2))

        visit(self)
        G.add_edge(pydot.Edge("start", id(self), label="", style="dashed"))

        return G

    def _repr_svg_(self):
        try:
            return self.graph().create_svg().decode("utf8")
        except Exception as e:
            print(e, e.__traceback__)
            pass

    def write_to(self, fname):
        return self.graph().write_svg(fname)


def lr0_formatter(state):
    try:
        return "\n".join(str(item)[:-4] for item in state)
    except TypeError:
        return str(state)[:-4]


def move(automaton, states, symbol):
    moves = set()
    for state in states:
        try:
            moves.update(automaton.transitions[state][symbol])
        except:
            pass
        # Your code here
    return moves


def epsilon_closure(automaton, states):
    pending = [s for s in states]  # equivalente a list(states) pero me gusta así :p
    closure = {s for s in states}  # equivalente a  set(states) pero me gusta así :p

    while pending:
        state = pending.pop()
        try:
            closure.update(automaton.transitions[state][""])
            for item in automaton.transitions[state][""]:
                pending.append(item)
        except:
            pass
        # Your code here

    return ContainerSet(*closure)


def nfa_to_dfa(automaton):
    transitions = {}

    start = epsilon_closure(automaton, [automaton.start])
    start.id = 0
    start.is_final = any(s in automaton.finals for s in start)
    states = [start]

    pending = [start]
    count = 1
    while pending:
        state = pending.pop()
        for symbol in automaton.vocabulary:
            # Your code here
            # ...
            U = epsilon_closure(automaton, move(automaton, state, symbol))
            if U == set():
                continue
            try:
                U = states[states.index(U)]
            except ValueError:
                U.id = len(states)
                U.is_final = any(s in automaton.finals for s in U)
                pending.append(U)
                states.append(U)
            try:
                transitions[state.id, symbol]
                assert False, "Invalid DFA!!!"
            except KeyError:
                transitions[state.id, symbol] = U.id
                # Your code here
                pass

    finals = [state.id for state in states if state.is_final]
    dfa = DFA(len(states), finals, transitions)
    return dfa


def NFA_evaluate(automaton, string):
    current = epsilon_closure(automaton, [automaton.start])

    for symbol in string:
        current = epsilon_closure(automaton, move(automaton, current, symbol))

    return any(s in automaton.finals for s in current)

