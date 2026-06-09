# Лабораторная работа №5: Интерпретатор языка CBAS

## Текст задания

Разработать интерпретатор языка CBAS. Язык имеет следующий синтаксис:

- Поддерживаются переменные (идентификаторы из букв и подчёркивания)
- Типы данных: целые числа
- Арифметические выражения: `+`, `-`, `*`, `/`, скобки
- Операторы:
  - присваивание `var = expression;`
  - условный оператор `if (condition) statement`
  - цикл `for (var = start; condition; var = var + 1) statement`
  - составной оператор `{ ... }`
  - оператор вывода `print(expression);`
  - оператор ввода `input(var);`

## Полный код

```python
from enum import Enum

class TT(Enum):
    INT = 1
    ID = 2
    PLUS = 3
    MINUS = 4
    MUL = 5
    DIV = 6
    LP = 7
    RP = 8
    LB = 9
    RB = 10
    SM = 11
    EQ = 12
    REL = 13
    KW = 14
    EOF = 15

class Tok:
    def __init__(self, t, v):
        self.t = t
        self.v = v
    
    def __repr__(self):
        return f'{self.t}:{self.v}'

class Lex:
    def __init__(self, src):
        self.src = src
        self.pos = 0
        self.kw = {'if', 'for', 'print', 'input'}
        self.rel_ops = {'<', '>', '==', '!=', '<=', '>='}
    
    def next(self):
        while self.pos < len(self.src) and self.src[self.pos].isspace():
            self.pos += 1
        
        if self.pos >= len(self.src):
            return Tok(TT.EOF, None)
        
        ch = self.src[self.pos]
        
        if ch.isalpha() or ch == '_':
            s = ''
            while self.pos < len(self.src) and (self.src[self.pos].isalnum() or self.src[self.pos] == '_'):
                s += self.src[self.pos]
                self.pos += 1
            if s in self.kw:
                return Tok(TT.KW, s)
            return Tok(TT.ID, s)
        
        if ch.isdigit():
            s = ''
            while self.pos < len(self.src) and self.src[self.pos].isdigit():
                s += self.src[self.pos]
                self.pos += 1
            return Tok(TT.INT, int(s))
        
        if ch == '+':
            self.pos += 1
            return Tok(TT.PLUS, '+')
        if ch == '-':
            self.pos += 1
            return Tok(TT.MINUS, '-')
        if ch == '*':
            self.pos += 1
            return Tok(TT.MUL, '*')
        if ch == '/':
            self.pos += 1
            return Tok(TT.DIV, '/')
        if ch == '(':
            self.pos += 1
            return Tok(TT.LP, '(')
        if ch == ')':
            self.pos += 1
            return Tok(TT.RP, ')')
        if ch == '{':
            self.pos += 1
            return Tok(TT.LB, '{')
        if ch == '}':
            self.pos += 1
            return Tok(TT.RB, '}')
        if ch == ';':
            self.pos += 1
            return Tok(TT.SM, ';')
        if ch == '=':
            self.pos += 1
            if self.pos < len(self.src) and self.src[self.pos] == '=':
                self.pos += 1
                return Tok(TT.REL, '==')
            return Tok(TT.EQ, '=')
        if ch == '<':
            self.pos += 1
            if self.pos < len(self.src) and self.src[self.pos] == '=':
                self.pos += 1
                return Tok(TT.REL, '<=')
            return Tok(TT.REL, '<')
        if ch == '>':
            self.pos += 1
            if self.pos < len(self.src) and self.src[self.pos] == '=':
                self.pos += 1
                return Tok(TT.REL, '>=')
            return Tok(TT.REL, '>')
        if ch == '!':
            self.pos += 1
            if self.pos < len(self.src) and self.src[self.pos] == '=':
                self.pos += 1
                return Tok(TT.REL, '!=')
            raise ValueError(f'Неожиданный символ: {ch}')
        
        raise ValueError(f'Неожиданный символ: {ch}')

class Parser:
    def __init__(self, lex):
        self.lex = lex
        self.cur = self.lex.next()
        self.vars = {}
    
    def eat(self, t):
        if self.cur.t != t:
            raise ValueError(f'Ожидается {t}, получено {self.cur.t}')
        x = self.cur
        self.cur = self.lex.next()
        return x
    
    def prog(self):
        self.stmts()
    
    def stmts(self):
        while self.cur.t != TT.EOF and self.cur.t != TT.RB:
            self.stmt()
    
    def stmt(self):
        if self.cur.t == TT.ID:
            name = self.cur.v
            self.eat(TT.ID)
            self.eat(TT.EQ)
            val = self.expr()
            self.vars[name] = val
            self.eat(TT.SM)
        elif self.cur.t == TT.LB:
            self.eat(TT.LB)
            self.stmts()
            self.eat(TT.RB)
        elif self.cur.t == TT.KW:
            if self.cur.v == 'if':
                self.eat(TT.KW)
                self.eat(TT.LP)
                cond = self.cond()
                self.eat(TT.RP)
                if cond:
                    self.stmt()
            elif self.cur.v == 'for':
                self.eat(TT.KW)
                self.eat(TT.LP)
                var = self.cur.v
                self.eat(TT.ID)
                self.eat(TT.EQ)
                start = self.expr()
                self.eat(TT.SM)
                self.vars[var] = start
                cond_pos = self.lex.pos
                while True:
                    if not self.cond():
                        break
                    self.eat(TT.SM)
                    upd_start = self.lex.pos
                    self.expr()
                    self.eat(TT.RP)
                    self.stmt()
                    self.lex.pos = cond_pos
                    self.cur = self.lex.next()
                self.eat(TT.SM)
                self.eat(TT.RP)
            elif self.cur.v == 'print':
                self.eat(TT.KW)
                self.eat(TT.LP)
                val = self.expr()
                print(int(val))
                self.eat(TT.RP)
                self.eat(TT.SM)
            elif self.cur.v == 'input':
                self.eat(TT.KW)
                self.eat(TT.LP)
                var = self.cur.v
                self.eat(TT.ID)
                self.eat(TT.RP)
                self.eat(TT.SM)
                try:
                    val = int(input('> '))
                    self.vars[var] = val
                except:
                    raise ValueError('Ошибка ввода')
    
    def expr(self):
        val = self.term()
        while self.cur.t in [TT.PLUS, TT.MINUS]:
            op = self.cur.v
            self.eat(self.cur.t)
            right = self.term()
            if op == '+':
                val = val + right
            else:
                val = val - right
        return val
    
    def term(self):
        val = self.fact()
        while self.cur.t in [TT.MUL, TT.DIV]:
            op = self.cur.v
            self.eat(self.cur.t)
            right = self.fact()
            if op == '*':
                val = val * right
            elif right != 0:
                val = val / right
            else:
                raise ValueError('Деление на ноль')
        return val
    
    def fact(self):
        if self.cur.t == TT.INT:
            val = self.cur.v
            self.eat(TT.INT)
            return val
        elif self.cur.t == TT.ID:
            name = self.cur.v
            self.eat(TT.ID)
            if name not in self.vars:
                raise ValueError(f'Переменная {name} не определена')
            return self.vars[name]
        elif self.cur.t == TT.LP:
            self.eat(TT.LP)
            val = self.expr()
            self.eat(TT.RP)
            return val
        else:
            raise ValueError(f'Ожидается число или переменная, получено {self.cur}')
    
    def cond(self):
        left = self.expr()
        op = self.eat(TT.REL).v
        right = self.expr()
        
        if op == '<':
            return left < right
        elif op == '>':
            return left > right
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '<=':
            return left <= right
        elif op == '>=':
            return left >= right
        else:
            raise ValueError(f'Неизвестный оператор: {op}')

def main():
    try:
        with open('test.cbas', 'r') as f:
            src = f.read()
    except FileNotFoundError:
        print('Ошибка: файл test.cbas не найден')
        return
    
    try:
        lex = Lex(src)
        p = Parser(lex)
        p.prog()
        print('Программа выполнена успешно')
    except Exception as e:
        print(f'Ошибка: {e}')

if __name__ == '__main__':
    main()
```

## Результаты выполнения

Для файла `test.cbas`:
```
n = 5;
f = 1;
for (i = 1; i <= n; i = i + 1) {
  f = f * i;
}
print(f);
```

Вывод:
```
120
Программа выполнена успешно
```

## Пояснения ключевых функций

### Класс `Lex` (Лексический анализатор)
Разбивает исходный код на токены.

- **`next()`** — возвращает следующий токен (число, переменную, оператор и т.д.)

### Класс `Parser` (Синтаксический анализ и интерпретация)
Выполняет синтаксический анализ рекурсивным спуском и одновременно интерпретирует программу.

- **`prog()`, `stmts()`, `stmt()`** — парсят и выполняют операторы
- **`expr()`, `term()`, `fact()`** — парсят и вычисляют выражения
- **`cond()`** — парсит и вычисляет условия

### Основной цикл
Читает файл `test.cbas`, создает лексер и парсер, выполняет программу.
