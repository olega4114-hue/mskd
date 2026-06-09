# Лабораторная работа №1: Калькулятор арифметических выражений

## Текст задания

Написать программу-аналог калькулятора. Входная строка — произвольное арифметическое выражение, содержащее:

- знаки операций `+`, `-`, `*`, `/`
- скобки `(`, `)`
- действительные числа (например, 12, 66.6, .54, 221)
- имя встроенной функции от двух переменных: `log(a,b)` (логарифм a по основанию b)

Программа должна:
- проверить корректность выражения (баланс скобок, допустимые символы, правильность записи чисел и функции)
- вычислить значение выражения с учётом приоритета операций (обычная математика) и поддержкой функции `log`
- обрабатывать исключения (деление на ноль, log от неположительных чисел, неверные аргументы)
- при ошибке выдать информацию о типе и позиции ошибки

Алгоритм: обратная польская запись (ОПЗ).

## Полный код

```python
import math
import re

def tokenize(expr):
    expr = expr.replace(' ', '')
    if not expr:
        raise ValueError('Пустое выражение')
    
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isdigit() or (expr[i] == '.' and i + 1 < len(expr) and expr[i + 1].isdigit()):
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            tokens.append(expr[i:j])
            i = j
        elif expr[i:i+3] == 'log':
            tokens.append('log')
            i += 3
        elif expr[i] in '+-*/(),':
            tokens.append(expr[i])
            i += 1
        else:
            raise ValueError(f'Недопустимый символ: {expr[i]}')
    
    return tokens

def check_syntax(tokens):
    if not tokens:
        raise ValueError('Пустое выражение')
    
    paren = 0
    for i, t in enumerate(tokens):
        if t == '(':
            paren += 1
        elif t == ')':
            paren -= 1
            if paren < 0:
                raise ValueError('Несоответствие скобок')
        
        if t == 'log':
            if i + 1 >= len(tokens) or tokens[i + 1] != '(':
                raise ValueError('Ошибка синтаксиса log')
    
    if paren != 0:
        raise ValueError('Несоответствие скобок')

def prec(op):
    return {'+': 1, '-': 1, '*': 2, '/': 2}.get(op, 0)

def to_rpn(tokens):
    check_syntax(tokens)
    
    out = []
    ops = []
    i = 0
    
    while i < len(tokens):
        t = tokens[i]
        
        try:
            f = float(t)
            out.append(('num', f))
        except:
            if t == '(':
                ops.append(t)
            elif t == ')':
                while ops and ops[-1] != '(':
                    out.append(('op', ops.pop()))
                if not ops:
                    raise ValueError('Несоответствие скобок')
                ops.pop()
                if ops and ops[-1] == 'log':
                    out.append(('func', ops.pop()))
            elif t in ['+', '-', '*', '/']:
                while ops and ops[-1] != '(' and ops[-1] != 'log' and prec(ops[-1]) >= prec(t):
                    out.append(('op', ops.pop()))
                ops.append(t)
            elif t == 'log':
                ops.append(t)
            elif t == ',':
                while ops and ops[-1] != '(':
                    out.append(('op', ops.pop()))
        
        i += 1
    
    while ops:
        o = ops.pop()
        if o == '(':
            raise ValueError('Несоответствие скобок')
        if o == 'log':
            out.append(('func', o))
        else:
            out.append(('op', o))
    
    return out

def eval_rpn(rpn):
    stk = []
    
    for item_type, val in rpn:
        if item_type == 'num':
            stk.append(val)
        elif item_type == 'op':
            if len(stk) < 2:
                raise ValueError('Ошибка вычисления')
            b = stk.pop()
            a = stk.pop()
            
            if val == '+':
                stk.append(a + b)
            elif val == '-':
                stk.append(a - b)
            elif val == '*':
                stk.append(a * b)
            elif val == '/':
                if b == 0:
                    raise ValueError('Деление на ноль')
                stk.append(a / b)
        elif item_type == 'func':
            if val == 'log':
                if len(stk) < 2:
                    raise ValueError('Ошибка вычисления')
                b = stk.pop()
                a = stk.pop()
                if a <= 0 or b <= 0 or b == 1:
                    raise ValueError('Неверный аргумент функции log')
                stk.append(math.log(a, b))
    
    if len(stk) != 1:
        raise ValueError('Ошибка вычисления')
    
    return stk[0]

def calc(expr):
    tokens = tokenize(expr)
    rpn = to_rpn(tokens)
    return eval_rpn(rpn)

if __name__ == '__main__':
    while True:
        try:
            s = input('> ').strip()
            if not s or s.lower() == 'exit':
                break
            r = calc(s)
            print(f'Результат: {r}')
        except ValueError as e:
            print(f'Ошибка: {e}')
        except Exception as e:
            print(f'Ошибка: {e}')
```

## Результаты выполнения

### Пример 1
```
> (2+3)*log(100,10)
Результат: 10.0
```

### Пример 2
```
> 2.5 * 4
Результат: 10.0
```

### Пример 3
```
> (5+5)/0
Ошибка: Деление на ноль
```

### Пример 4
```
> log(0,10)
Ошибка: Неверный аргумент функции log
```

### Пример 5
```
> (2+3)*5 - 10/2
Результат: 20.0
```

## Пояснения ключевых функций

### `tokenize(expr)`
Разбивает входную строку на токены (числа, операции, скобки, функции). Проверяет наличие недопустимых символов.

### `check_syntax(tokens)`
Проверяет синтаксическую корректность: баланс скобок и правильность синтаксиса функции `log(a,b)`.

### `prec(op)`
Возвращает приоритет операции для определения порядка вычисления.

### `to_rpn(tokens)`
Конвертирует инфиксную нотацию в обратную польскую запись (RPN) с помощью алгоритма сортировочной станции.

### `eval_rpn(rpn)`
Вычисляет значение выражения, представленного в обратной польской записи, используя стек. Обрабатывает все операции и функцию `log`.
