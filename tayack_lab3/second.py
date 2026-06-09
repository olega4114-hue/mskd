import re


class Transition:
    def __init__(self, state, input, stack, is_terminal=False):
        self.state = state
        self.input = input
        self.stack = stack
        self.index = -1
        self.is_terminal = is_terminal


class TransitionArgs:
    def __init__(self, state, input_symbol, stack_symbol):
        self.state = state
        self.input_symbol = input_symbol
        self.stack_symbol = stack_symbol


class StackValue:
    def __init__(self, state, content):
        self.state = state
        self.content = content


class Command:
    def __init__(self, args, values):
        self.args = args
        self.values = values


class AutomatonStorage:
    def __init__(self, filename):
        self.input_symbols = set()
        self.non_terminal_symbols = set()
        self.initial_state = '0'
        self.initial_stack_symbol = '|'
        self.empty_symbol = '\0'
        self.commands = []
        self.transition_chain = []

        with open(filename, 'r') as file:
            exp = re.compile(r'([A-Z])>([ -~]+)')
            for line in file:
                if not line.strip():
                    continue

                match = exp.match(line.strip())
                if not match or line[-1] == '|' or line[2] == '|':
                    raise RuntimeError("Не удалось распознать синтаксис входного файла")
                else:
                    self.non_terminal_symbols.add(match[1])
                    self.commands.append(Command(TransitionArgs(self.initial_state, self.empty_symbol, match[1]),
                                                 [StackValue(self.initial_state, "")]))

                    for c in match[2]:
                        if c == '|':
                            if self.commands[-1].values[-1].content:
                                self.commands[-1].values.append(StackValue(self.initial_state, ""))
                        else:
                            self.input_symbols.add(c)
                            self.commands[-1].values[-1].content += c

                    for value in self.commands[-1].values:
                        value.content = value.content[::-1]

        for c in self.non_terminal_symbols:
            self.input_symbols.discard(c)

        for c in self.input_symbols:
            self.commands.append(
                Command(TransitionArgs(self.initial_state, c, c), [StackValue(self.initial_state, "\0")]))

        self.commands.append(Command(TransitionArgs(self.initial_state, self.empty_symbol, self.initial_stack_symbol),
                                     [StackValue(self.initial_state, "\0")]))

    def display_info(self):
        print("Входные алфавиты:\nP = {", ', '.join(self.input_symbols), "}")
        print("Алфавит нетерминальных символов:\nZ = {", ', '.join(self.non_terminal_symbols), "h0}")
        print("\nСписок команд:")
        for cmd in self.commands:
            input_sym = 'lambda' if cmd.args.input_symbol == self.empty_symbol else cmd.args.input_symbol
            stack_sym = 'h0' if cmd.args.stack_symbol == self.initial_stack_symbol else cmd.args.stack_symbol
            print(f"f(s{cmd.args.state}, {input_sym}, {stack_sym}) = ", end="")
            for v in cmd.values:
                content = 'lambda' if v.content[0] == self.empty_symbol else v.content
                print(f"(s{v.state}, {content}); ", end="")
            print()

    def display_transition_chain(self):
        print("\nЦепочка переходов: ")
        for transition in self.transition_chain:
            input_sym = 'lambda' if not transition.input else transition.input
            print(f"(s{transition.state}, {input_sym}, h0{transition.stack}) | ", end="")
        print("(s0, lambda, lambda)")

    def push_transition(self):
        chain_size = len(self.transition_chain)
        for cmd in self.commands:
            command_size = len(self.transition_chain[-1].stack)
            if (self.transition_chain and
                    self.transition_chain[-1].state == cmd.args.state and
                    (self.transition_chain[-1].input[
                         0] == cmd.args.input_symbol or self.empty_symbol == cmd.args.input_symbol) and
                    self.transition_chain[-1].stack[command_size - 1] == cmd.args.stack_symbol):

                for value in cmd.values:
                    new_transition = Transition(value.state, self.transition_chain[-1].input,
                                                self.transition_chain[-1].stack)
                    if cmd.args.input_symbol != self.empty_symbol:
                        new_transition.input = new_transition.input[::-1][1:][::-1]

                    new_transition.stack = new_transition.stack[:-1] + value.content
                    self.transition_chain.append(new_transition)

                    if len(self.transition_chain[-1].input) < len(self.transition_chain[-1].stack):
                        self.transition_chain.pop()
                        return False
                    if not self.transition_chain[-1].input and not self.transition_chain[-1].stack:
                        return True
                    if self.push_transition():
                        return True
        self.transition_chain.pop()
        return False

    def check_input_line(self, input_line):
        self.transition_chain.append(Transition(self.initial_state, input_line, ''))
        self.transition_chain[0].stack += self.commands[0].args.stack_symbol

        result = self.push_transition()
        if result:
            print("Валидная строка")
            self.display_transition_chain()
        else:
            print("Невалидная строка")

        self.transition_chain.clear()
        return result


if __name__ == "__main__":
    try:
        file_num = input("Грамматика: ")
        storage = AutomatonStorage(f"grammar{file_num}.txt")
        storage.display_info()

        while True:
            input_line = input("Введите строку: ")
            storage.check_input_line(input_line)
            print()

    except Exception as e:
        print(e)
