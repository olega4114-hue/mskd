import re
from collections import defaultdict


class State:
    def __init__(self, name, is_final=False):
        self.name = name
        self.is_final = is_final
        self.transitions = defaultdict(list)  # Словарь переходов: символ -> список состояний

    def add_transition(self, symbol, state):
        self.transitions[symbol].append(state)

    def __repr__(self):
        return f"State({self.name}, final={self.is_final}, transitions={dict(self.transitions)})"


class FiniteAutomaton:
    def __init__(self):
        self.states = {}  # Словарь состояний: имя -> состояние
        self.start_state = None

    def add_transition(self, from_state, symbol, to_state):
        if from_state not in self.states:
            self.states[from_state] = State(from_state)
        if to_state not in self.states:
            is_final = to_state.startswith('f')
            self.states[to_state] = State(to_state, is_final)

        self.states[from_state].add_transition(symbol, self.states[to_state])

    def is_deterministic(self):
        """Проверяет детерминированность автомата"""
        for state in self.states.values():
            for symbol, transitions in state.transitions.items():
                if len(transitions) > 1:
                    return False
        return True

    def determinize(self):
        """Детерминирует недетерминированный автомат"""
        new_transitions = {}
        new_states = {}
        state_queue = [frozenset([self.start_state])]  # Начинаем с множества, содержащего стартовое состояние
        new_start_state_name = ','.join(sorted([self.start_state.name]))

        while state_queue:
            current_set = state_queue.pop(0)
            current_name = ','.join(sorted([state.name for state in current_set]))

            if current_name not in new_states:
                new_states[current_name] = State(current_name)

            for symbol in {sym for state in current_set for sym in state.transitions.keys()}:
                next_states = frozenset(
                    [next_state for state in current_set for next_state in state.transitions[symbol]])
                next_state_name = ','.join(sorted([s.name for s in next_states]))

                if next_state_name not in new_states:
                    new_states[next_state_name] = State(next_state_name, any(s.is_final for s in next_states))
                    state_queue.append(next_states)

                new_states[current_name].add_transition(symbol, new_states[next_state_name])

        self.states = new_states
        self.start_state = new_states[new_start_state_name]

    def analyze_string(self, input_string):
        current_state = self.start_state
        for symbol in input_string:
            if symbol in current_state.transitions:
                current_state = current_state.transitions[symbol][0]
            else:
                return False
        return current_state.is_final

    def print_transitions(self):
        for state_name, state in self.states.items():
            for symbol, next_states in state.transitions.items():
                for next_state in next_states:
                    print(f"{state_name},{symbol}={next_state.name}")


def parse_automaton(file_path):
    automaton = FiniteAutomaton()
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            match = re.match(r'(q|f)(\d+),(\w)=(q|f)(\d+)', line)
            if match:
                from_state_type, from_state_num, symbol, to_state_type, to_state_num = match.groups()
                from_state = f"{from_state_type}{from_state_num}"
                to_state = f"{to_state_type}{to_state_num}"
                automaton.add_transition(from_state, symbol, to_state)

    automaton.start_state = automaton.states['q0']
    return automaton


# Пример использования
file_path = 'nondet_automaton2.txt'
# input_string = "ab"
input_string = 'abbbbbbbbbbbbbbbbm'

# Чтение автомата
automaton = parse_automaton(file_path)

# Проверка детерминированности
if automaton.is_deterministic():
    print("Автомат детерминирован.")
else:
    print("Автомат недетерминирован.")
    print("Таблица переходов недетерминированного автомата:")
    automaton.print_transitions()
    print("Детерминирование автомата...")
    automaton.determinize()

# Проверка строки
result = automaton.analyze_string(input_string)
if result:
    print(f"Строка '{input_string}' допускается автоматом.")
else:
    print(f"Строка '{input_string}' не допускается автоматом.")

print("Таблица переходов автомата после детерминирования:")
automaton.print_transitions()
