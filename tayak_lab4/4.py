class Token:
    def __init__(self, type=None, value=None, line=0):
        self.type = type
        self.value = value
        self.line = line

TokenType = ['TOKEN_INT', 'TOKEN_BOOL', 'TOKEN_VOID',
             'TOKEN_MAIN', 'TOKEN_FOR', 'TOKEN_IF', 'TOKEN_RETURN',
             'TOKEN_IDENTIFIER', 'TOKEN_NUMBER', 'TOKEN_INCREMENT'
             'TOKEN_ASSIGN', 'TOKEN_SEMICOLON', 'TOKEN_LBRACE', 'TOKEN_RBRACE', 'TOKEN_AND', 'TOKEN_OR'
             'TOKEN_LPAREN', 'TOKEN_RPAREN', 'TOKEN_RELOP', 'TOKEN_EOF', 'TOKEN_UNKNOWN']

class Lexer:
    def __init__(self, filename):
        with open(f'{filename}.txt', 'r') as file:
            self.file_content = file.read()
        self.line = 1
        self.currentchar = self.get_char()  # Инициализируем первый символ

    def isEOF(self):
        return self.currentchar == ''  # Теперь мы проверяем currentchar

    def get_char(self):
        if len(self.file_content) == 0:
            return ''  # Возвращаем пустую строку для обозначения EOF
        res = self.file_content[0]
        self.file_content = self.file_content[1:]
        return res

    def skipWhiteSpace(self):
        while self.currentchar.isspace():
            if self.currentchar == '\n':
                self.line += 1
            self.currentchar = self.get_char()  # Переход к следующему символу

    def nextToken(self):
        self.skipWhiteSpace()

        if self.isEOF():
            return Token("EOF", "", self.line)

        if self.currentchar.isalpha() or self.currentchar == '_':
            identifier = ''
            while self.currentchar.isalnum() or self.currentchar == '_':
                identifier += self.currentchar
                self.currentchar = self.get_char()
            if identifier in ["int", "bool", "void"]:
                return Token("TYPE", identifier, self.line)
            if identifier == "main":
                return Token("MAIN", "main", self.line)
            if identifier == "for":
                return Token("FOR", "for", self.line)
            if identifier == "if":
                return Token("IF", "if", self.line)
            if identifier == "return":
                return Token("RETURN", "return", self.line)
            if identifier in ["true", "false"]:
                return Token("BOOL", identifier, self.line)
            if identifier == "and":
                return Token("AND", "and", self.line)
            if identifier == "or":
                return Token("OR", "or", self.line)
            return Token("IDENTIFIER", identifier, self.line)

        if self.currentchar.isdigit():
            number = ''
            while self.currentchar.isdigit():
                number += self.currentchar
                self.currentchar = self.get_char()
            return Token("NUMBER", number, self.line)

        if self.currentchar == '=':
            self.currentchar = self.get_char()
            if self.currentchar == '=':
                self.currentchar = self.get_char()
                return Token("RELOP", "==", self.line)
            return Token("ASSIGN", "=", self.line)

        if self.currentchar == '<':
            self.currentchar = self.get_char()
            return Token("RELOP", "<", self.line)
        if self.currentchar == '>':
            self.currentchar = self.get_char()
            return Token("RELOP", ">", self.line)
        if self.currentchar == '!':
            self.currentchar = self.get_char()
            if self.currentchar == '=':
                self.currentchar = self.get_char()
                return Token("RELOP", "!=", self.line)

        # Добавляем поддержку оператора ++
        if self.currentchar == '+':
            self.currentchar = self.get_char()
            if self.currentchar == '+':
                self.currentchar = self.get_char()
                return Token("INCREMENT", "++", self.line)

        if self.currentchar == ';':
            self.currentchar = self.get_char()
            return Token("SEMICOLON", ";", self.line)
        if self.currentchar == '{':
            self.currentchar = self.get_char()
            return Token("LBRACE", "{", self.line)
        if self.currentchar == '}':
            self.currentchar = self.get_char()
            return Token("RBRACE", "}", self.line)
        if self.currentchar == '(':
            self.currentchar = self.get_char()
            return Token("LPAREN", "(", self.line)
        if self.currentchar == ')':
            self.currentchar = self.get_char()
            return Token("RPAREN", ")", self.line)

        unknown = self.currentchar
        self.currentchar = self.get_char()
        return Token("UNKNOWN", unknown, self.line)


class Parser:
    def __init__(self, filename):
        self.lexer = Lexer(filename)
        self.errorCount = 0
        self.currentToken = self.lexer.nextToken()
        self.symbolTable = {}
        self.function_type = None
        self.inBraces = 0

    def advance(self):
        print(f"ADVANCE: текущий токен {self.currentToken.type}, значение {self.currentToken.value}")
        self.currentToken = self.lexer.nextToken()

    def error(self, message, expected=None):
        print('\n')
        print('----------------------------------------------------------------------------------------------------')
        print(f'Ошибка в строке {self.currentToken.line}: {message} (текущий токен: {self.currentToken.value}, {self.currentToken.type})')
        print('----------------------------------------------------------------------------------------------------')
        print('\n')
        self.errorCount += 1
        if expected:
            pass
            #self.panicMode(expected)
        else:
            self.advance()

    # def panicMode(self, expected):
    #     print(f"EXPECTED PANIC {expected}")
    #     while self.currentToken.type not in expected and self.currentToken.type != "EOF":
    #         self.advance()
    #     print(f"PANIC OUT: текущий токен {self.currentToken.type}")

    def expect(self, expectedType):
        print(f"EXPECT: ожидается {expectedType}, текущий токен {self.currentToken.type}")
        if self.currentToken.type == expectedType:
            self.advance()
        else:
            self.error(f"Ожидался {expectedType}", {expectedType})

    def program(self):
        self.type(True)
        self.expect("MAIN")
        self.expect("LPAREN")
        self.expect("RPAREN")
        self.expect("LBRACE")
        # self.declaration()
        # self.expect('SEMICOLON')
        # self.declaration()
        # self.expect('SEMICOLON')
        self.statement()
        self.expect("RBRACE")

    def type(self, function):
        if self.currentToken.type == "TYPE":
            if function:
                self.function_type = self.currentToken.value
            print(f"TYPE: найден тип {self.currentToken.value}")
            self.advance()
        else:
            self.error("Ожидался тип данных (int, bool или void)")


    #-----------------------------------------------------------------------------------------MAINSTATEMENT
    def statement(self):
        if self.currentToken.type == "LBRACE":
            self.inBraces += 1
            # print('=====================================================================================================')
            self.advance()
            while self.currentToken.type != "RBRACE" and self.currentToken.type != "EOF":
                self.statement()
            if self.currentToken.type == "RBRACE":
                self.inBraces -=1
            self.expect("RBRACE")
            self.statement()
        elif self.currentToken.type == "FOR":
            self.advance()
            self.forStatement()
        elif self.currentToken.type == "IF":
            # print('----------------------------------------------------------------------------------------------------')
            self.advance()
            self.ifStatement()
            #self.advance()
            self.statement()
        elif self.currentToken.type == "RETURN":
            self.advance()
            success = self.returnStatement()
            if not success:
                self.advance()
        else:
            print(f"DECLARATION: текущий токен {self.currentToken.type}")
            self.declaration()
            self.expect("SEMICOLON")
            if self.inBraces == 0:
                self.statement()


    def returnStatement(self):
        returnType = self.function_type
        print(f"RETURN: ожидается {returnType}, текущий тип функции {self.function_type}")

        if self.currentToken.type == "NUMBER":
            if returnType != "int":
                self.error("Несоответствие типов: ожидается " + returnType + ", но возвращено число.")
                return False
            self.advance()
        elif self.currentToken.type == "BOOL":
            if returnType != "bool":
                self.error("Несоответствие типов: ожидается " + returnType + ", но возвращено булевое значение.")
                return False
            self.advance()
        elif self.currentToken.type == "IDENTIFIER":
            varName = self.currentToken.value
            if varName not in self.symbolTable:
                self.error("Переменная " + varName + " не объявлена.", {"SEMICOLON"})
                return False
            elif self.symbolTable[varName] != returnType:
                self.error("Несоответствие типов: ожидается " + returnType + ", но возвращена переменная типа " + self.symbolTable[varName] + ".")
                return False
            self.advance()
        else:
            self.error("Некорректное возвращаемое значение.")
            return False

        self.expect("SEMICOLON")
        return True

    def declaration(self):
        varType = self.currentToken.value
        self.type(False)
        varName = self.currentToken.value
        print(f"DECLARATION: переменная {varName} типа {varType}")
        self.expect("IDENTIFIER")
        self.symbolTable[varName] = varType
        self.expect("ASSIGN")
        self.assign(varName)

    def assign(self, varName):
        varType = self.symbolTable[varName]
        print(f"ASSIGN: переменная {varName} типа {varType}")

        if self.currentToken.type == "NUMBER":
            if varType != "int":
                self.error("Несоответствие типов: переменной " + varName + " (типа " + varType + ") присваивается число.")
                return
            self.advance()
        elif self.currentToken.type == "IDENTIFIER":
            assignedVar = self.currentToken.value
            if assignedVar not in self.symbolTable:
                self.error("Переменная " + assignedVar + " не объявлена.", {"SEMICOLON"})
            elif self.symbolTable[assignedVar] != varType:
                self.error("Несоответствие типов: переменной " + varName + " (типа " + varType + ") присваивается значение переменной " + assignedVar + " (типа " + self.symbolTable[assignedVar] + ").")
                return
            self.advance()
        elif self.currentToken.type == "BOOL":
            if varType != "bool":
                self.error("Несоответствие типов: переменной " + varName + " (типа " + varType + ") присваивается булевое значение.")
                return
            self.advance()
        else:
            self.error("Ожидался идентификатор, число или булевое значение после '='", {"NUMBER", "IDENTIFIER", "BOOL"})

    def forStatement(self):
        print("FOR STATEMENT BEGIN")
        self.expect("LPAREN")
        self.declaration()
        self.expect("SEMICOLON")
        self.boolExpression()
        self.expect("SEMICOLON")
        self.incrementExpression()
        self.expect("RPAREN")
        self.statement()
        print("FOR STATEMENT END")

    def incrementExpression(self):
        print("INCREMENT EXPRESSION BEGIN")
        if self.currentToken.type == "IDENTIFIER":
            varName = self.currentToken.value
            if varName not in self.symbolTable:
                self.error("Переменная " + varName + " не объявлена.", {"SEMICOLON"})
            self.advance()
            self.expect("INCREMENT")
        else:
            self.error("Ожидалось выражение инкремента, например i++")
        print("INCREMENT EXPRESSION END")

    def boolExpression(self):
        print("BOOL EXPRESSION BEGIN")
        self.simpleExpression()
        while self.currentToken.type in {"AND", "OR"}:
            logical_op = self.currentToken.type
            print(f"LOGICAL OPERATOR: {logical_op}")
            self.advance()
            self.simpleExpression()
        print("BOOL EXPRESSION END")

    def simpleExpression(self):
        if self.currentToken.type == "IDENTIFIER":
            varName = self.currentToken.value
            if varName not in self.symbolTable:
                self.error("Переменная " + varName + " не объявлена.", {"SEMICOLON"})
            self.advance()
        elif self.currentToken.type == "NUMBER":
            self.advance()
        else:
            self.error("Ожидался идентификатор или число", {"IDENTIFIER", "NUMBER"})

        self.expect("RELOP")

        if self.currentToken.type == "IDENTIFIER":
            varName = self.currentToken.value
            if varName not in self.symbolTable:
                self.error("Переменная " + varName + " не объявлена.", {"SEMICOLON"})
            self.advance()
        elif self.currentToken.type == "NUMBER":
            self.advance()
        else:
            self.error("Ожидался идентификатор или число после оператора отношения")

    def ifStatement(self):
        self.expect("LPAREN")
        self.boolExpression()
        self.expect("RPAREN")

    def parse(self):
        self.program()
        if self.errorCount == 0:
            print("Синтаксический анализ успешно завершен.")
        else:
            print(f"Обнаружено ошибок: {self.errorCount}")


# Запуск парсера
print('start')
filename = '4'
parser = Parser(filename)
parser.parse()
