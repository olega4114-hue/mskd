
class Token:
    def __init__(self):
        self.type
        self.value
        self.line

TokenType = ['TOKEN_INT', 'TOKEN_BOOL', 'TOKEN_VOID',
'TOKEN_MAIN', 'TOKEN_FOR', 'TOKEN_IF', 'TOKEN_RETURN',
'TOKEN_IDENTIFIER', 'TOKEN_NUMBER',
'TOKEN_ASSIGN', 'TOKEN_SEMICOLON', 'TOKEN_LBRACE', 'TOKEN_RBRACE',
'TOKEN_LPAREN', 'TOKEN_RPAREN', 'TOKEN_RELOP', 'TOKEN_EOF', 'TOKEN_UNKNOWN']

class Lexer:
    file_content = None
    line = 0
    # currentchar = None
    currentchar = ''

    def __init__(self, filename):
        with open(f'{filename}.txt', 'r') as file:
            self.file_content = file.read()

    def isEOF(self):
        return len(self.file_content) == 0

    def get_char(self):
        res = self.file_content[0]
        self.file_content = self.file_content[1:]
        return res

    def skipWhiteSpace(self):
        while self.currentchar == ' ':
            if self.currentchar == '\n':
                self.line += 1
            self.currentchar = self.get_char()


    def nextToken(self):
        self.skipWhiteSpace()

        #КОНЕЦ ФАЙЛА
        if self.isEOF():
            return ['EOF', '', self.line]

        #ИДЕНТИФИКАТОР
        if self.currentchar.isalpha() or self.currentchar == '_':
            idetifier = ''
            while self.currentchar.isalnum() or self.currentchar == '_':
                idetifier += self.currentchar
                self.currentchar = self.get_char()

            if idetifier == 'int':
                return ['TYPE', 'int', self.line]
            if idetifier == 'bool':
                return ['TYPE', 'bool', self.line]
            if idetifier == 'void':
                return ['TYPE', 'void', self.line]
            if idetifier == 'main':
                return ['MAIN', 'main', self.line]
            if idetifier == 'for':
                return ['FOR', 'for', self.line]
            if idetifier == 'if':
                return ['IF', 'if', self.line]
            if idetifier == 'return':
                return ['RETURN', 'return', self.line]

            if idetifier == 'true' or idetifier == 'false':
                return ['BOOL', idetifier, self.line]

            return ['IDENTIFIER', idetifier, self.line]

        #ЧИСЛО
        if self.currentchar.isdigit():
            number = ''
            while self.currentchar.isdigit():
                number+=self.currentchar
                self.currentchar = self.get_char()

            return ['NUMBER', number, self.line]

        #ОПЕРАТОРЫ
        if self.currentchar == '=':
            self.currentchar = self.get_char()
            if self.currentchar == '=':
                self.currentchar = self.get_char()
                return ['RELOP', '==', self.line]
            return ['ASSING', '=', self.line]

        if self.currentchar == '<':
            self.currentchar = self.get_char()
            return ['RELOP', '<', self.line]
        if self.currentchar == '>':
            self.currentchar = self.get_char()
            return ['RELOP', '>', self.line]
        if self.currentchar == '!':
            self.currentchar = self.get_char()
            if self.currentchar == '=':
                self.currentchar = self.get_char()
                return ['RELOP', '!=', self.line]

        #РАЗДЕЛИТЕЛИ
        if self.currentchar == ';':
            self.currentchar = self.get_char()
            return ['SEMICOLON', ';', self.line]
        if self.currentchar == '{':
            self.currentchar = self.get_char()
            return ['LBRACE', '{', self.line]
        if self.currentchar == '}':
            self.currentchar = self.get_char()
            return ['RBRACE', '}', self.line]
        if self.currentchar == '(':
            self.currentchar = self.get_char()
            return ['LPAREN', '(', self.line]
        if self.currentchar == ')':
            self.currentchar = self.get_char()
            return ['RPAREN', ')', self.line]

        unknown = self.currentchar
        self.currentchar = self.get_char()
        return ['UNKNOWN', unknown, self.line]


class Parser:
    lexer = None
    currentToken = None
    errorCount = 0
    symbolTable = {}
    function_type = None

    def __init__(self, filename):
        self.lexer = Lexer(filename)
        self.errorCount = 0
        self.currentToken = self.lexer.nextToken()


    def advance(self):
        self.currentToken = self.lexer.nextToken()

    def error(self, message):
        print(f'Ошибка в строке: {self.currentToken[2]} : {message} : токен {self.currentToken[1]}')
        self.errorCount += 1
        self.panicMode()

    def error2(self, message, expected):
        print(f'Ощибка в строке: {self.currentToken[2]} : {message} : токен {self.currentToken[1]}')
        self.errorCount += 1
        self.panicMode2(expected)

    def panicMode(self):
        print(f'PANIC {self.currentToken[0]}')
        self.advance()
        print(f'PANIC 2 {self.currentToken[0]}')

    def panicMode2(self, expected):
        print('EXPECT PANIC ')
        for i in expected:
            print(i)

        while self.currentToken[0] not in expected and self.currentToken[0] != 'EOF':
            self.advance()

        print(f'EXPECTED PANIC OUT 1 {self.currentToken[0]}')

    #ПРОВЕРКА И ОЖИДАНИЕ ТОКЕНА
    def expect(self, expectedType):
        print(f'EXPECT {expectedType} {self.currentToken[0]}')
        if self.currentToken[0] == expectedType:
            self.advance()
        else:
            self.error2(f'Ожидался {expectedType}', {expectedType})

    def program(self):
        self.type(True)
        self.expect('MAIN')
        self.expect('LPAREN')
        self.expect('RPAREN')
        self.expect('LBRACE')
        self.statement()
        self.expect('RBRACE')

    def type(self, function):
        if self.currentToken[0] == 'TYPE':
            if function:
                self.function_type = self.currentToken[1]
            self.advance()
        else:
            self.error('Ожидался тип данных (int, bool или void)')

    def statement(self):
        if self.currentToken[0] == 'LBRACE':
            self.advance()
            while self.currentToken[0] != 'RBRACE' and self.currentToken[0] != 'EOF':
                self.statement()
            self.expect('RBRACE')
        elif self.currentToken[0] == 'FOR':
            self.advance()
            self.forStatement()
            self.statement()
        elif self.currentToken[0] == 'IF':
            self.advance()
            self.ifStatement()
            self.statement()
        elif self.currentToken[0] == 'RETURN':
            self.advance()
            success = self.returnStatement()
            if not success:
                self.advance()
        elif self.currentToken[0] == 'RBRACE':
            self.advance()
        else:
            print(f'DECLARATION {self.currentToken[0]}')
            self.declaration()
            self.expect('SEMICOLON')

    def returnStatement(self):
        returnType = self.function_type

        if self.currentToken[0] == 'NUMBER':
            if returnType != 'int':
                self.error("Несоответствие типов: ожидается " + returnType + ", но возвращено число.")
                return False
            self.advance()
        elif self.currentToken == 'BOOL':
            if returnType != 'BOOL':
                self.error("Несоответствие типов: ожидается " + returnType + ", но возвращено булевое значение.")
                return False
            self.advance()
        elif self.currentToken[0] == 'IDENTIFIER':
            varName = self.currentToken[1]
            if varName not in self.symbolTable:
                self.error2("Переменная " + varName + " не объявлена.", {"SEMICOLON"})
                return False
            elif self.symbolTable[varName] != returnType:
                self.error("Несоответствие типов: ожидается " + returnType + ", но возвращена переменная типа " + self.symbolTable[varName] + ".")
                return False
            self.advance()

        else:
            self.error("Некорректное возвращаемое значение.")
            return False

        self.expect('SEMICOLON')

        return True

    def declaration(self):
        varType = self.currentToken[1]
        self.type(False)
        varName = self.currentToken[1]
        self.expect('IDENTIFIER')
        self.symbolTable[varName] = varType
        self.expect('ASSIGN')
        self.assign(varName)

    def assign(self, varName):
        varType = self.symbolTable[varName]

        if self.currentToken[0] == 'NUMBER':
            if varType != 'int':
                self.error("Несоответствие типов: переменной " + varName + " (типа " + varType + ") присваивается число.")
                return
            self.advance()
        elif self.currentToken[0] == 'IDENTIFIER':
            assignedVar = self.currentToken[1]

            if assignedVar not in self.symbolTable:
                self.error2("Переменная " + assignedVar + " не объявлена.",  {"SEMICOLON"} )
            elif self.symbolTable[assignedVar] != varType:
                self.error("Несоответствие типов: переменной " + varName + " (типа " + varType + ") присваивается значение переменной " + assignedVar + " (типа " + self.symbolTable[assignedVar] + ").")
                return
            self.advance()
        elif self.currentToken[0] == 'BOOL':
            if varType != 'bool':
                self.error("Несоответствие типов: переменной " + varName + " (типа " + varType + ") присваивается булевое значение.")
                return
            self.advance()
        else:
            self.error2("Ожидался идентификатор, число или булевое значение после '='", { "NUMBER", "IDENTIFIER", "BOOL" })

    def forStatement(self):
        self.expect('LPAREN')
        self.declaration()
        self.expect('SEMICOLON')
        self.boolExpression()
        self.expect('SEMICOLON')
        self.expect('RPAREN')
        self.statement()

    def boolExpression(self):
        #firsOperandType = ''

        if self.currentToken[0] == 'IDENTIFIER':
            varName = self.currentToken[1]

            if varName not in self.symbolTable:
                self.error2("Переменная " + varName + " не объявлена.", { "SEMICOLON" })
            firstOperandType = self.symbolTable[varName]
            self.advance()
        elif self.currentToken[0] == 'NUMBER':
            firstOperandType = 'int'
            self.advance()
        else:
            self.error2("Ожидалось выражение типа <bool_expression>", { "IDENTIFIER", "NUMBER" })
            return

        self.expect("RELOP")

        if self.currentToken[0] == 'IDENTIFIER':
            secondVarName = self.currentToken[1]

            if secondVarName not in self.symbolTable:
                self.error2("Переменная " + secondVarName + " не объявлена.", { "SEMICOLON" })
                print("ASSIGN " + self.currentToken[1])
            elif self.symbolTable[secondVarName] != firstOperandType:
                self.error("Несоответствие типов в булевом выражении: " + firstOperandType + " и " + self.symbolTable[secondVarName])
        elif self.currentToken[0] == 'NUMBER':
            secondVarName = self.currentToken[1]
            self.advance()
        else:
            self.error("Ожидался идентификатор после оператора отношения.")

    def ifStatement(self):
        self.expect('LPAREN')
        self.boolExpression()
        self.expect('RPAREN')

    def parse(self):
        self.program()
        if self.errorCount == 0:
            print("Синтаксический анализ успешно завершен.")
        else:
            print(f"Обнаружено ошибок: {self.errorCount}" )


#--------------------------------------------------------------------
filename = '1'
parser = Parser(filename)
parser.parse()















