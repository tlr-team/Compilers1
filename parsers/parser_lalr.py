from .parser_abstract import ShiftReduceParser
from .parser_lr import LR1
from automaton import  State
from tools import empty_formatter

class LALR(LR1):
    def _mergue_items_lookaheads(self, items, others):
        if len(items) != len(others):
            return False

        new_lookaheads = []
        for item in items:
            for item2 in others:
                if item.Center() == item2.Center():
                    new_lookaheads.append(item2.lookaheads)
                    break
            else:
                return False

        for item, new_lookahead in zip(items, new_lookaheads):
            item.lookaheads = item.lookaheads.union(new_lookahead)

        return True

    def _build_automaton(self): #build_LR1_automaton
        super()._build_automaton()

        states = list(self.automaton)
        new_states = []
        visited = {}

        for i, state in enumerate(states):
            if state not in visited:
                # creates items
                items = [item.Center() for item in state.state]

                # check for states with same center
                for state2 in states[i:]:
                    if self._mergue_items_lookaheads(items, state2.state):
                        visited[state2] = len(new_states)

                # add new state
                new_states.append(State(frozenset(items), True))

        # making transitions
        for state in states:
            new_state = new_states[visited[state]]
            for symbol, transitions in state.transitions.items():
                for state2 in transitions:
                    new_state2 = new_states[visited[state2]]
                    # check if the transition already exists
                    if symbol not in new_state.transitions or new_state2 not in new_state.transitions[symbol]:
                        new_state.add_transition(symbol, new_state2)

        new_states[0].set_formatter(empty_formatter)
        self.automaton = new_states[0]
        # self.parse_corrupted
