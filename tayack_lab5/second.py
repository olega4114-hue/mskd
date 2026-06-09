import re
from collections import defaultdict


class Lexer:
    def __init__(self, source_code):
        self.tokens = self.tokenize(source_code)
        self.current_token_index = 0

    def tokenize(self, code):
        token_specification = [
            ("KEYWORD", r'\b(print|scan|for|if|else|to)\b'),  # Ключевые слова
            ("IDENTIFIER", r'[a-zA-Z_][a-zA-Z0-9_]*'),  # Идентификаторы
            ("NUMBER", r'\d+'),  # Числа
            ("STRING", r'"[^"]*"'),  # Строки
            ("OP", r'[+\-*/=!<>]+'),  # Операторы
            ("LPAREN", r'\('),  # Левая скобка
            ("RPAREN", r'\)'),  # Правая скобка
            ("LBRACE", r'\{'),  # Левая фигурная скобка
            ("RBRACE", r'\}'),  # Правая фигурная скобка
            ("SEMICOLON", r';'),  # Точка с запятой
            ("COMMA", r','),  # Запятая
            ("WHITESPACE", r'[ \t\n]+'),  # Пробелы
            ("MISMATCH", r'.'),  # Остальные символы
        ]
        token_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_specification)
        tokens = []
        for match in re.finditer(token_regex, code):
            kind = match.lastgroup
            value = match.group()
            if kind == "WHITESPACE":
                continue
            elif kind == "MISMATCH":
                raise ValueError(f"Unexpected character {value}")
            tokens.append((kind, value))
        print("TOKENS:", tokens)  # Отладка токенов
        return tokens

    def next_token(self):
        if self.current_token_index < len(self.tokens):
            token = self.tokens[self.current_token_index]
            self.current_token_index += 1
            return token
        return None

    def peek_token(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None

    def push_back(self):
        self.current_token_index = max(0, self.current_token_index - 1)


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.symbol_table = defaultdict(int)


    def parse(self):
        while (token := self.lexer.next_token()) is not None:
            if token[0] == "KEYWORD" and token[1] == "print":
                self.handle_print()
            elif token[0] == "KEYWORD" and token[1] == "scan":
                self.handle_scan()
            elif token[0] == "IDENTIFIER":
                self.handle_assignment(token[1])
            elif token[0] == "KEYWORD" and token[1] == "for":
                self.handle_for()
            elif token[0] == "KEYWORD" and token[1] == "if":
                self.handle_if()
            elif token[0] == "RBRACE":
                # Завершаем блок, если встречаем закрывающую скобку
                return
            else:
                raise SyntaxError(f"Unexpected token: {token}")

    def handle_print(self):
        while True:
            token = self.lexer.next_token()
            if token[0] == "STRING":
                print(token[1][1:-1], end=" ")  # Удаляем кавычки и печатаем строку
            elif token[0] == "IDENTIFIER":
                print(self.symbol_table[token[1]], end=" ")  # Печатаем значение переменной
            elif token[0] == "NUMBER":
                print(int(token[1]), end=" ")  # Печатаем число
            else:
                raise SyntaxError(f"Unexpected token in print statement: {token}")

            # Проверяем следующий токен: либо продолжение (запятая), либо завершение (точка с запятой)
            next_token = self.lexer.peek_token()
            if next_token and next_token[0] == "COMMA":
                self.lexer.next_token()  # Пропускаем запятую и продолжаем
            elif next_token and next_token[0] == "SEMICOLON":
                self.lexer.next_token()  # Пропускаем точку с запятой и завершаем
                print()  # Завершаем строку вывода
                break
            else:
                raise SyntaxError(f"Expected ',' or ';' in print statement, got {next_token}")

    def handle_scan(self):
        token = self.lexer.next_token()
        if token[0] != "IDENTIFIER":
            raise SyntaxError("Expected variable name after 'scan'")
        self.symbol_table[token[1]] = int(input(f"Enter value for {token[1]}: "))
        self.expect_token("SEMICOLON")

    def handle_assignment(self, variable):
        self.expect_token("OP", "=")
        value = self.parse_expression()
        self.symbol_table[variable] = value
        self.expect_token("SEMICOLON")

    def handle_for(self):
        loop_var = self.lexer.next_token()[1]
        self.expect_token("OP", "=")
        start = self.parse_expression()
        self.expect_token("KEYWORD", "to")
        end = self.parse_expression()
        self.expect_token("LBRACE")

        old_value = self.symbol_table[loop_var]
        for i in range(start, end + 1):
            self.symbol_table[loop_var] = i
            self.parse()
        self.symbol_table[loop_var] = old_value

    def handle_if(self):
        condition = self.parse_boolean_expression()  # Вычисление условия
        self.expect_token("LBRACE")  # Ожидаем открывающую скобку для блока if

        # Если условие истинно, выполняем блок if
        if condition:
            self.parse()  # Вставляем блок для выполнения внутри if
        self.expect_token("RBRACE")  # Ожидаем закрывающую скобку для блока if

        # После блока if, проверяем наличие else
        token = self.lexer.peek_token()
        if token and token[0] == "KEYWORD" and token[1] == "else":
            self.lexer.next_token()  # Пропускаем 'else'
            self.expect_token("LBRACE")  # Ожидаем открывающую скобку для блока else

            # Если условие if было ложным, выполняем блок else
            if not condition:
                self.parse()  # Вставляем блок для выполнения внутри else
            self.expect_token("RBRACE")  # Ожидаем закрывающую скобку для блока else

    def parse_expression(self):
        token = self.lexer.next_token()
        if token[0] == "NUMBER":
            return int(token[1])
        elif token[0] == "IDENTIFIER":
            return self.symbol_table[token[1]]
        else:
            raise SyntaxError(f"Unexpected token in expression: {token}")

    def parse_boolean_expression(self):
        left = self.parse_expression()
        op = self.lexer.next_token()[1]
        right = self.parse_expression()
        if op == "==":
            return left == right
        elif op == "!=":
            return left != right
        elif op == "<":
            return left < right
        elif op == ">":
            return left > right
        else:
            raise SyntaxError(f"Unknown boolean operator: {op}")

    def expect_token(self, token_type, value=None):
        token = self.lexer.next_token()
        if token is None or token[0] != token_type or (value and token[1] != value):
            raise SyntaxError(f"Expected {token_type} {value}, got {token}")


if __name__ == "__main__":
    with open('easy_program.txt', 'r') as file:
        source_code = file.read()

    lexer = Lexer(source_code)
    parser = Parser(lexer)
    parser.parse()
