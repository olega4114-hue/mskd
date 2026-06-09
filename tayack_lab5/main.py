import re
from collections import defaultdict

class Lexer:
    def __init__(self, source_code):
        self.tokens = self.tokenize(source_code)
        self.current_token_index = 0

    def tokenize(self, code):
        token_specification = [
            ("KEYWORD", r'\b(print|scan|for|if|else|to)\b'),  # Ключевые слова
            ("IDENTIFIER", r'[a-zA-Z_][a-zA-Z0-9_]*'),        # Идентификаторы
            ("NUMBER", r'\d+'),                               # Числа
            ("STRING", r'"[^"]*"'),                           # Строки
            ("OP", r'[+\-*/=!<>]+'),                          # Операторы
            ("LPAREN", r'\('),                                # Левая скобка
            ("RPAREN", r'\)'),                                # Правая скобка
            ("LBRACE", r'\{'),                                # Левая фигурная скобка
            ("RBRACE", r'\}'),                                # Правая фигурная скобка
            ("SEMICOLON", r';'),                              # Точка с запятой
            ("COMMA", r','),                                  # Запятая
            ("WHITESPACE", r'[ \t\n]+'),                      # Пробелы
            ("MISMATCH", r'.'),                               # Остальные символы
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
        #print("TOKENS:", tokens)  # Отладка токенов
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
    def __init__(self, lexer : Lexer):
        self.lexer = lexer
        self.symbol_table = defaultdict(int)

    def parse(self):

        #print('\n----------------------------------------PROGRAM START--------------------------------------------------------------------------------\n')

        while (token := self.lexer.next_token()) is not None:
            if token[0] == 'KEYWORD' and token[1] == 'print':
                self.handle_print()
            elif token[0] == 'KEYWORD' and token[1] == 'scan':
                self.handle_scan()
            elif token[0] == 'IDENTIFIER':
                self.handle_assignment(token[1])
            elif token[0] == 'KEYWORD' and token[1] == 'for':
                self.handle_for()
            elif token[0] == 'KEYWORD' and token[1] == 'if':
                self.handle_if()
            else:
                raise SyntaxError(f'Unexpected token {token}')

        #print('\n----------------------------------------PROGRAM END----------------------------------------------------------------------------------\n')

    def handle_scan(self):
        token = self.lexer.next_token()
        if token[0] != 'IDENTIFIER':
            raise SyntaxError("Expected variable name after 'scan'")
        self.symbol_table[token[1]] = int(input(f'Enter value for {token[1]}: '))
        self.expect_token('SEMICOLON')

    def handle_print(self):
        result_parts = []
        while True:
            token = self.lexer.peek_token()
            if token[0] == 'STRING':
                self.lexer.next_token()
                result_parts.append(token[1][1:-1])  # Убираем кавычки
            elif token[0] == 'NUMBER' or token[0] == 'IDENTIFIER' or token[0] == 'LPAREN':
                result_parts.append(str(self.parse_expression()))
            else:
                raise SyntaxError(f'Unexpected token in print: {token}')

            next_token = self.lexer.peek_token()
            if next_token and next_token[0] == 'COMMA':
                self.lexer.next_token()  # Пропустить запятую
            elif next_token and next_token[0] == 'SEMICOLON':
                self.lexer.next_token()  # Пропустить точку с запятой
                print(" ".join(result_parts))
                break
            else:
                raise SyntaxError(f'Expected COMMA or SEMICOLON in print statement, got {next_token}')

    def handle_if(self):
        condition = self.parse_boolean_expression()  # Вычисление условия
        self.expect_token("LBRACE")  # Ожидаем открывающую скобку для блока if

        # Собираем токены для блока if
        if_body_tokens = []
        brace_count = 1  # Считаем количество открытых фигурных скобок
        while brace_count > 0:
            token = self.lexer.next_token()
            if token is None:
                raise SyntaxError("Unclosed brace in if block")
            if token[0] == "LBRACE":
                brace_count += 1
            elif token[0] == "RBRACE":
                brace_count -= 1
            if brace_count > 0:
                if_body_tokens.append(token)

        # Проверяем наличие блока else
        else_body_tokens = []
        token = self.lexer.peek_token()
        if token and token[0] == "KEYWORD" and token[1] == "else":
            self.lexer.next_token()  # Пропускаем 'else'
            self.expect_token("LBRACE")  # Ожидаем открывающую скобку для блока else

            brace_count = 1  # Считаем количество открытых фигурных скобок для else
            while brace_count > 0:
                token = self.lexer.next_token()
                if token is None:
                    raise SyntaxError("Unclosed brace in else block")
                if token[0] == "LBRACE":
                    brace_count += 1
                elif token[0] == "RBRACE":
                    brace_count -= 1
                if brace_count > 0:
                    else_body_tokens.append(token)

        # Выполнение соответствующего блока
        if condition:
            self.execute_block(if_body_tokens)
        elif else_body_tokens:
            self.execute_block(else_body_tokens)

    def execute_block(self, tokens):
        """Выполняет список токенов как отдельный блок."""
        block_lexer = Lexer(" ".join(token[1] for token in tokens))
        block_parser = Parser(block_lexer)
        block_parser.symbol_table = self.symbol_table  # Передаем текущую таблицу символов
        block_parser.parse()

    def handle_for(self):
        loop_var = self.lexer.next_token()[1]
        self.expect_token('OP', '=')
        start = self.parse_expression()
        self.expect_token('KEYWORD', 'to')
        end = self.parse_expression()
        self.expect_token('LBRACE')

        # Сохраняем текущую позицию в токенах для тела цикла
        loop_body_tokens = []
        brace_count = 1  # Считаем количество открытых фигурных скобок
        while brace_count > 0:
            token = self.lexer.next_token()
            if token is None:
                raise SyntaxError("Unclosed brace in for loop body")
            if token[0] == "LBRACE":
                brace_count += 1
            elif token[0] == "RBRACE":
                brace_count -= 1
            if brace_count > 0:
                loop_body_tokens.append(token)

        old_value = self.symbol_table[loop_var]
        for i in range(start, end):
            self.symbol_table[loop_var] = i
            # Создаем временный лексер для тела цикла
            body_lexer = Lexer(" ".join(token[1] for token in loop_body_tokens))
            body_parser = Parser(body_lexer)
            body_parser.symbol_table = self.symbol_table  # Передаем текущую таблицу символов
            body_parser.parse()

        self.symbol_table[loop_var] = old_value

    def handle_assignment(self, variable):
        self.expect_token('OP', '=')
        value = self.parse_expression()
        self.symbol_table[variable] = value
        self.expect_token('SEMICOLON')

    def parse_expression(self):
        return self.parse_term()

    def parse_term(self):
        """Парсинг выражений с операциями сложения и вычитания."""
        node = self.parse_factor()
        while (token := self.lexer.peek_token()) and token[1] in ('+', '-'):
            self.lexer.next_token()  # Пропускаем оператор
            right = self.parse_factor()
            if token[1] == '+':
                node += right
            elif token[1] == '-':
                node -= right
        return node

    def parse_factor(self):
        """Парсинг выражений с операциями умножения и деления."""
        node = self.parse_primary()
        while (token := self.lexer.peek_token()) and token[1] in ('*', '/'):
            self.lexer.next_token()  # Пропускаем оператор
            right = self.parse_primary()
            if token[1] == '*':
                node *= right
            elif token[1] == '/':
                if right == 0:
                    raise ZeroDivisionError("Division by zero")
                node /= right
        return node

    def parse_primary(self):
        """Парсинг чисел, переменных и подвыражений в скобках."""
        token = self.lexer.next_token()
        if token[0] == 'NUMBER':
            return int(token[1])
        elif token[0] == 'IDENTIFIER':
            if token[1] in self.symbol_table:
                return self.symbol_table[token[1]]
            else:
                raise ValueError(f"Undefined variable {token[1]}")
        elif token[1] == '(':
            # Подвыражение в скобках
            value = self.parse_expression()
            self.expect_token('RPAREN', ')')
            return value
        else:
            raise SyntaxError(f"Unexpected token in primary expression: {token}")

    def parse_boolean_expression(self):
        left = self.parse_expression()
        op = self.lexer.next_token()[1]
        right = self.parse_expression()
        if op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '<':
            return left < right
        elif op == '>':
            return left > right
        else:
            raise SyntaxError(f'Unknown boolean operator: {op}')

    def expect_token(self, token_type, value=None):
        token = self.lexer.next_token()
        if token is None or token[0] != token_type or (value and token[1] != value):
            raise SyntaxError(f'Expected {token_type} {value}, got {token}')

if __name__ == "__main__":
    with open('expression2_program.txt', 'r') as file:
        source_code = file.read()

    lexer = Lexer(source_code)
    parser = Parser(lexer)
    parser.parse()
