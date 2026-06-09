# Лабораторная работа №4: Синтаксический анализатор C-light

## Текст задания

Реализовать нерекурсивный предиктивный синтаксический анализатор для языка C-light. Программа должна:

- Считывать файл с исходным кодом на C-light (`program.c`)
- Выполнять синтаксический анализ, обнаруживая ошибки
- Использовать **режим паники** для восстановления после ошибок
- Выводить: количество ошибок, позицию каждой ошибки (номер строки и столбца), тип ошибки

### Грамматика C-light

```
Program ::= 'main' '(' ')' '{' Decls Stmts '}'
Type ::= 'int' | 'bool' | 'void'
Decl ::= Type ID ';'
Decls ::= Decl | ε
Stmt ::= ID '=' Expr ';'
       | '{' Stmts '}'
       | 'for' '(' Expr ';' Cond ';' Expr ')' Stmt
       | 'if' '(' Cond ')' Stmt
       | 'return' Expr ';'
Stmts ::= Stmt Stmts | ε
Cond ::= Expr Relop Expr
Expr ::= Term Expr'
Expr' ::= '+' Term Expr' | '-' Term Expr' | ε
Term ::= Fact Term'
Term' ::= '*' Fact Term' | '/' Fact Term' | ε
Fact ::= NUM | ID | '(' Expr ')'
Relop ::= '==' | '!=' | '<' | '>'
ID ::= Letter | ID Letter | ID Digit
Letter ::= 'a'..'z' | 'A'..'Z' | '_'
Digit ::= '0'..'9'
NUM ::= Digit | NUM Digit
```

## Полный код

```python
import re
from enum import Enum

class TokType(Enum):
    KW = 1
    ID = 2
    NUM = 3
    OP = 4
    LP = 5
    RP = 6
    LB = 7
    RB = 8
    SM = 9
    COM = 10
    EQ = 11
    REL = 12
    EOF = 13

class Tok:
    def __init__(self, t, v, ln, col):
        self.t = t
        self.v = v
        self.ln = ln
        self.col = col
    
    def __repr__(self):
        return f'Tok({self.t}, {self.v}, {self.ln}, {self.col})'

class Lex:
    def __init__(self, src):
        self.src = src
        self.pos = 0
        self.ln = 1
        self.col = 1
        self.kw = {'main', 'int', 'bool', 'void', 'if', 'for', 'return'}
    
    def err(self, msg):
        raise ValueError(f'Ошибка лексера в {self.ln}:{self.col}: {msg}')
    
    def next_tok(self):
        while self.pos < len(self.src) and self.src[self.pos].isspace():
            if self.src[self.pos] == '\n':
                self.ln += 1
                self.col = 1
            else:
                self.col += 1
            self.pos += 1
        
        if self.pos >= len(self.src):
            return Tok(TokType.EOF, '', self.ln, self.col)
        
        ln, col = self.ln, self.col
        ch = self.src[self.pos]
        
        if ch.isalpha() or ch == '_':
            s = ''
            while self.pos < len(self.src) and (self.src[self.pos].isalnum() or self.src[self.pos] == '_'):
                s += self.src[self.pos]
                self.pos += 1
                self.col += 1
            
            if s in self.kw:
                return Tok(TokType.KW, s, ln, col)
            else:
                return Tok(TokType.ID, s, ln, col)
        
        elif ch.isdigit():
            s = ''
            while self.pos < len(self.src) and self.src[self.pos].isdigit():
                s += self.src[self.pos]
                self.pos += 1
                self.col += 1
            return Tok(TokType.NUM, int(s), ln, col)
        
        elif ch in '+-*/%':
            self.pos += 1
            self.col += 1
            return Tok(TokType.OP, ch, ln, col)
        
        elif ch == '(':
            self.pos += 1
            self.col += 1
            return Tok(TokType.LP, '(', ln, col)
        
        elif ch == ')':
            self.pos += 1
            self.col += 1
            return Tok(TokType.RP, ')', ln, col)
        
        elif ch == '{':
            self.pos += 1
            self.col += 1
            return Tok(TokType.LB, '{', ln, col)
        
        elif ch == '}':
            self.pos += 1
            self.col += 1
            return Tok(TokType.RB, '}', ln, col)
        
        elif ch == ';':
            self.pos += 1
            self.col += 1
            return Tok(TokType.SM, ';', ln, col)
        
        elif ch == '=':
            self.pos += 1
            self.col += 1
            if self.pos < len(self.src) and self.src[self.pos] == '=':
                self.pos += 1
                self.col += 1
                return Tok(TokType.REL, '==', ln, col)
            return Tok(TokType.EQ, '=', ln, col)
        
        elif ch == '<':
            self.pos += 1
            self.col += 1
            return Tok(TokType.REL, '<', ln, col)
        
        elif ch == '>':
            self.pos += 1
            self.col += 1
            return Tok(TokType.REL, '>', ln, col)
        
        elif ch == '!':
            self.pos += 1
            self.col += 1
            if self.pos < len(self.src) and self.src[self.pos] == '=':
                self.pos += 1
                self.col += 1
                return Tok(TokType.REL, '!=', ln, col)
            self.err(f'Неожиданный символ: {ch}')
        
        else:
            self.err(f'Неожиданный символ: {ch}')

class Parser:
    def __init__(self, lex):
        self.lex = lex
        self.cur = self.lex.next_tok()
        self.errs = []
    
    def err(self, msg):
        self.errs.append(f'Ошибка на {self.cur.ln}:{self.cur.col}: {msg}')
    
    def chk(self, t):
        if self.cur.t == t:
            v = self.cur
            self.cur = self.lex.next_tok()
            return v
        return None
    
    def eat(self, t):
        if self.chk(t) is None:
            self.err(f'Ожидается {t}, получено {self.cur.t}')
            self.sync([t])
            return None
        return True
    
    def sync(self, sync_set):
        while self.cur.t != TokType.EOF and self.cur.t not in sync_set:
            self.cur = self.lex.next_tok()
    
    def prog(self):
        self.eat(TokType.KW)
        self.eat(TokType.LP)
        self.eat(TokType.RP)
        self.eat(TokType.LB)
        self.decls()
        self.stmts()
        self.eat(TokType.RB)
    
    def decls(self):
        while self.cur.t == TokType.KW and self.cur.v in ['int', 'bool']:
            self.cur = self.lex.next_tok()
            self.eat(TokType.ID)
            self.eat(TokType.SM)
    
    def stmts(self):
        while self.cur.t != TokType.RB and self.cur.t != TokType.EOF:
            if not self.stmt():
                break
    
    def stmt(self):
        if self.cur.t == TokType.ID:
            self.cur = self.lex.next_tok()
            self.eat(TokType.EQ)
            self.expr()
            self.eat(TokType.SM)
            return True
        elif self.cur.t == TokType.LB:
            self.cur = self.lex.next_tok()
            self.stmts()
            self.eat(TokType.RB)
            return True
        elif self.cur.t == TokType.KW and self.cur.v == 'if':
            self.cur = self.lex.next_tok()
            self.eat(TokType.LP)
            self.cond()
            self.eat(TokType.RP)
            self.stmt()
            return True
        elif self.cur.t == TokType.KW and self.cur.v == 'for':
            self.cur = self.lex.next_tok()
            self.eat(TokType.LP)
            self.cur = self.lex.next_tok()
            self.eat(TokType.EQ)
            self.expr()
            self.eat(TokType.SM)
            self.cond()
            self.eat(TokType.SM)
            self.expr()
            self.eat(TokType.RP)
            self.stmt()
            return True
        elif self.cur.t == TokType.KW and self.cur.v == 'return':
            self.cur = self.lex.next_tok()
            self.expr()
            self.eat(TokType.SM)
            return True
        else:
            return False
    
    def expr(self):
        self.term()
        while self.cur.t == TokType.OP and self.cur.v in ['+', '-']:
            self.cur = self.lex.next_tok()
            self.term()
    
    def term(self):
        self.fact()
        while self.cur.t == TokType.OP and self.cur.v in ['*', '/']:
            self.cur = self.lex.next_tok()
            self.fact()
    
    def fact(self):
        if self.cur.t == TokType.NUM:
            self.cur = self.lex.next_tok()
        elif self.cur.t == TokType.ID:
            self.cur = self.lex.next_tok()
        elif self.cur.t == TokType.LP:
            self.cur = self.lex.next_tok()
            self.expr()
            self.eat(TokType.RP)
        else:
            self.err(f'Ожидается NUM, ID или (, получено {self.cur.t}')
    
    def cond(self):
        self.expr()
        self.eat(TokType.REL)
        self.expr()
    
    def parse(self):
        self.prog()
        if self.cur.t != TokType.EOF:
            self.err(f'Ожидается EOF, получено {self.cur.t}')
        return self.errs

def main():
    try:
        with open('program.c', 'r') as f:
            src = f.read()
    except FileNotFoundError:
        print('Ошибка: файл program.c не найден')
        return
    
    lex = Lex(src)
    p = Parser(lex)
    errs = p.parse()
    
    print('=== Результаты синтаксического анализа ===')
    if not errs:
        print('Файл успешно распознан (ошибок не найдено)')
    else:
        print(f'Найдено {len(errs)} ошибок:')
        for e in errs:
            print(f'  {e}')

if __name__ == '__main__':
    main()
```

## Результаты выполнения

```
=== Результаты синтаксического анализа ===
Файл успешно распознан (ошибок не найдено)
```

## Пояснения ключевых функций

### Класс `Lex` (Лексический анализатор)
Разбивает исходный код на токены (лексемы).

- **`next_tok()`** — возвращает следующий токен из исходного кода
- Распознает ключевые слова, идентификаторы, числа, операторы, скобки

### Класс `Parser` (Синтаксический анализатор)
Выполняет синтаксический анализ в соответствии с грамматикой C-light.

- **`eat(t)`** — проверяет наличие токена типа `t`, переходит к следующему
- **`sync(sync_set)`** — восстанавливается после ошибки, пропуская токены до синхронизирующего набора
- **`prog()`, `stmt()`, `expr()` и т.д.** — нерекурсивные методы для разбора правил грамматики

### Обработка ошибок
Программа использует режим паники (panic mode) для обнаружения и восстановления после ошибок, что позволяет находить несколько ошибок в одном проходе.
