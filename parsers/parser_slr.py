from .parser_abstract import ShiftReduceParser
from grammar import Item
from automaton import State, lr0_formatter
from tools import table_to_dataframe


class SLR(ShiftReduceParser):
    def _build_automaton(self): # _LR0_automaton
        assert len(self.startSymbol.productions) == 1, 'Grammar must be augmented'

        start_production = self.startSymbol.productions[0]
        start_item = Item(start_production, 0)

        automaton = State(start_item, True)

        pending = [ start_item ]
        visited = { start_item: automaton }

        while pending:
            current_item = pending.pop()
            if current_item.IsReduceItem:
                continue
            
            next_symbol = current_item.NextSymbol
            
            next_item = current_item.NextItem()
            if not next_item in visited:
                pending.append(next_item)
                visited[next_item] = State(next_item, True)
            
            if next_symbol.IsNonTerminal:
                for prod in next_symbol.productions:
                        next_item = Item(prod, 0)
                        if not next_item in visited:
                            pending.append(next_item)
                            visited[next_item] = State(next_item, True) 

            current_state = visited[current_item]
            
            current_state.add_transition(next_symbol.Name, visited[current_item.NextItem()])
            
            if next_symbol.IsNonTerminal:
                for prod in next_symbol.productions:
                        current_state.add_epsilon_transition(visited[Item(prod, 0)])
        self.automaton = automaton.to_deterministic(formatter=lr0_formatter)
        return automaton

    def _build_table(self):
        is_slr = True
        errors = ''
        for i, node in enumerate(self.automaton):
            print(i, node)
            node.idx = i
            node.tag = f"I{i}"

        for node in self.automaton:
            idx = node.idx
            for state in node.state:
                item = state.state
                if item.IsReduceItem:
                    prod = item.production
                    if prod.Left == self.startSymbol:
                        is_slr &= self._register(self.ACTION, idx, self.EOF.Name, (ShiftReduceParser.OK, None))
                    else:
                        for symbol in self.follows[prod.Left]:
                            is_slr &= self._register(self.ACTION, idx, symbol.Name, (ShiftReduceParser.REDUCE, prod))
                            errors += (
                                self._conflict_on(self.ACTION, idx, symbol) if not is_slr else ""
                            )               
                else:
                    next_symbol = item.NextSymbol
                    if next_symbol.IsTerminal:
                        is_slr &= self._register(self.ACTION, idx, next_symbol.Name, (ShiftReduceParser.SHIFT, node[next_symbol.Name][0].idx))
                        errors += (
                                self._conflict_on(self.ACTION, idx, next_symbol) if not is_slr else ""
                            )
                    else:
                        is_slr &= self._register(self.GOTO, idx, next_symbol.Name, node[next_symbol.Name][0].idx)
                        errors += self._conflict_on(self.GOTO, idx, next_symbol) if not is_slr else ""
                        
        self.errors = errors
        self._parse_corrupted = not is_slr


