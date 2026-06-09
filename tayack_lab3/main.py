import re

# Определение регулярных выражений для различных токенов
TOKEN_SPEC = [
    ('KEYWORD', r'\b(int|bool|void|for|if|return|main)\b'),
    ('NUMBER', r'\b\d+\b'),
    ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ('OP', r'[{}();=<>&|!+\-*/]'),  # добавлены +, -, *, /
    ('WS', r'\s+'),  # Пробельные символы (игнорируются)
    ('MISMATCH', r'.'),  # Любой другой символ вызывает ошибку
]

TOKEN_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)
token_re = re.compile(TOKEN_REGEX)

def tokenize(code):
    tokens = []
    for match in token_re.finditer(code):
        kind = match.lastgroup
        value = match.group()
        if kind == 'WS':
            continue
        elif kind == 'MISMATCH':
            raise SyntaxError(f'Unexpected character {value}')
        tokens.append((kind, value))
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = 0
        self.errors = []

    def parse(self):
        self.program()
        if not self.errors:
            print("No syntax errors found.")
        else:
            print("Errors found:")
            for error in self.errors:
                print(error)

    def program(self):
        self.expect('KEYWORD', 'int')     # Проверка типа для main
        self.expect('IDENTIFIER', 'main') # Проверка идентификатора main
        self.expect('OP', '(')            # Проверка открывающей скобки (
        self.expect('OP', ')')            # Проверка закрывающей скобки )
        self.expect('OP', '{')            # Проверка открывающей фигурной скобки {
        while self.get_token() and self.get_token()[1] != '}':
            self.statement()               # Переход к оператору
        self.expect('OP', '}')            # Проверка закрывающей фигурной скобки }

    def expect(self, kind, value=None):
        token = self.get_token()
        if not token:
            self.errors.append("Unexpected end of input")
            return
        if token[0] != kind or (value and token[1] != value):
            self.errors.append(f"Expected {value or kind} at position {self.current_token}, found {token}")
            self.panic()
        else:
            self.current_token += 1  # Переход к следующему токену только при успешном совпадении

    def get_token(self):
        if self.current_token < len(self.tokens):
            return self.tokens[self.current_token]
        return None

    def panic(self):
        # Пропуск токенов до подходящего
        while self.get_token() and self.get_token()[1] not in (';', '}', 'for', 'if', 'return'):
            self.current_token += 1

    def statement(self):
        token = self.get_token()
        if token and token[1] == '{':
            self.current_token += 1
            while self.get_token() and self.get_token()[1] != '}':
                self.statement()
            self.expect('OP', '}')
        elif token and token[1] == 'for':
            self.for_statement()
        elif token and token[1] == 'if':
            self.if_statement()
        elif token and token[1] == 'return':
            self.return_statement()
        elif token and token[0] == 'KEYWORD':
            self.declaration()
            self.expect('OP', ';')
        else:
            self.errors.append(f"Unexpected token {token} at position {self.current_token}")
            self.panic()

    def declaration(self):
        self.expect('KEYWORD')  # <type>
        self.expect('IDENTIFIER')  # <identifier>
        if self.get_token() and self.get_token()[1] == '=':
            self.current_token += 1
            self.assign_end()

    def assign_end(self):
        token = self.get_token()
        if token and token[0] in ('IDENTIFIER', 'NUMBER'):
            self.current_token += 1
        else:
            self.errors.append(f"Expected identifier or number at position {self.current_token}")
            self.panic()

    def for_statement(self):
        self.expect('KEYWORD', 'for')
        self.expect('OP', '(')
        self.declaration()
        self.expect('OP', ';')
        self.bool_expression()
        self.expect('OP', ';')
        self.assign_end()
        self.expect('OP', ')')
        self.statement()

    def if_statement(self):
        self.expect('KEYWORD', 'if')
        self.expect('OP', '(')
        self.bool_expression()
        self.expect('OP', ')')
        self.statement()

    def return_statement(self):
        self.expect('KEYWORD', 'return')
        self.expect('NUMBER')
        self.expect('OP', ';')

    def bool_expression(self):
        self.assign_end()
        self.relop()
        self.assign_end()

    def relop(self):
        token = self.get_token()
        if token and token[1] in ('<', '>', '==', '!='):
            self.current_token += 1
        else:
            self.errors.append(f"Expected relational operator at position {self.current_token}")
            self.panic()

def main():
    with open("2.txt", "r") as f:  # Обработка файла 1.txt
        code = f.read()
    tokens = tokenize(code)
    parser = Parser(tokens)
    parser.parse()

if __name__ == "__main__":
    main()
