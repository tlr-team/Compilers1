import pydot
from core.parser_tools import ContainerSet,lambda_productions
from core.grammar import Grammar

class NFA:
    def __init__(self, states, finals, transitions, start=0):
        self.states = states
        self.start = start
        self.finals = set(finals)
        self.map = transitions
        self.vocabulary = set()
        self.transitions = { state: {} for state in range(states) }
        self.regexs = {}
        
        for (origin, symbol), destinations in transitions.items():
            assert hasattr(destinations, '__iter__'), 'Invalid collection of states'
            self.transitions[origin][symbol] = destinations
            self.vocabulary.add(symbol)
            
        self.vocabulary.discard('')

        for org in self.transitions:
            for symb in self.transitions[org]:
                for dest in self.transitions[org][symb]:
                    try:
                        self.regexs[(org,dest)] += "|" + str(symb)
                    except KeyError:
                        self.regexs[(org,dest)] = str(symb)

        for key in self.regexs.keys():
            if len(self.regexs[key]) > 1:
                self.regexs[key] = "( " + self.regexs[key] + " )"
 
        
    def epsilon_transitions(self, state):
        assert state in self.transitions, 'Invalid state'
        try:
            return self.transitions[state]['']
        except KeyError:
            return ()
            
    def graph(self):
        G = pydot.Dot(rankdir='LR', margin=0.1)
        G.add_node(pydot.Node('start', shape='plaintext', label='', width=0, height=0))

        for (start, tran), destinations in self.map.items():
            tran = 'ε' if tran == '' else tran
            G.add_node(pydot.Node(start, shape='circle', style='bold' if start in self.finals else ''))
            for end in destinations:
                G.add_node(pydot.Node(end, shape='circle', style='bold' if end in self.finals else ''))
                G.add_edge(pydot.Edge(start, end, label=tran, labeldistance=2))

        G.add_edge(pydot.Edge('start', self.start, label='', style='dashed'))
        return G

    def _repr_svg_(self):
        try:
            return self.graph().create_svg().decode('utf8')
        except:
            pass

class DFA(NFA):
    
    def __init__(self, states, finals, transitions, start=0):
        assert all(isinstance(value, int) for value in transitions.values())
        assert all(len(symbol) > 0 for origin, symbol in transitions)
        
        transitions = { key: [value] for key, value in transitions.items() }
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
        #pass
    
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
    pending = [ s for s in states ] # equivalente a list(states) pero me gusta así :p
    closure = { s for s in states } # equivalente a  set(states) pero me gusta así :p
    
    while pending:
        state = pending.pop()
        try:
            closure.update(automaton.transitions[state][''])
            for item in automaton.transitions[state]['']:
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
    states = [ start ]

    pending = [ start ]
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
                assert False, 'Invalid DFA!!!'
            except KeyError:
                transitions[state.id, symbol] = U.id
                # Your code here
                pass
    
    finals = [ state.id for state in states if state.is_final ]
    dfa = DFA(len(states), finals, transitions)
    return dfa

def NFA_evaluate(automaton, string):
    current = epsilon_closure(automaton, [automaton.start])
    
    for symbol in string:
        current = epsilon_clousure(automaton, move(automaton, current, symbol))
    
    return any(s in automaton.finals for s in current)
    