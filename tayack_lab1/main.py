import math

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
            tokens.append(('NUM', float(expr[i:j])))
            i = j
        elif expr[i:i+3] == 'log':
            tokens.append(('LOG', 'log'))
            i += 3
        elif expr[i] in '+-*/':
            tokens.append(('OP', expr[i]))
            i += 1
        elif expr[i] == '(':
            tokens.append(('LP', '('))
            i += 1
        elif expr[i] == ')':
            tokens.append(('RP', ')'))
            i += 1
        elif expr[i] == ',':
            tokens.append(('COM', ','))
            i += 1
        else:
            raise ValueError(f'Недопустимый символ: {expr[i]}')
    
    return tokens

def prec(op):
    return {'+': 1, '-': 1, '*': 2, '/': 2}.get(op, 0)

def to_rpn(tokens):
    out = []
    ops = []
    
    for t, v in tokens:
        if t == 'NUM':
            out.append(('NUM', v))
        elif t == 'LOG':
            ops.append(('LOG', 'log'))
        elif t == 'OP':
            while ops and ops[-1][0] != 'LP' and ops[-1][0] != 'LOG':
                if prec(ops[-1][1]) >= prec(v):
                    out.append(ops.pop())
                else:
                    break
            ops.append(('OP', v))
        elif t == 'LP':
            ops.append(('LP', '('))
        elif t == 'RP':
            while ops and ops[-1][0] != 'LP':
                out.append(ops.pop())
            if not ops:
                raise ValueError('Несоответствие скобок')
            ops.pop()
            if ops and ops[-1][0] == 'LOG':
                out.append(ops.pop())
        elif t == 'COM':
            while ops and ops[-1][0] != 'LP':
                out.append(ops.pop())
    
    while ops:
        o = ops.pop()
        if o[0] == 'LP':
            raise ValueError('Несоответствие скобок')
        out.append(o)
    
    return out

def eval_rpn(rpn):
    stk = []
    
    for t, v in rpn:
        if t == 'NUM':
            stk.append(v)
        elif t == 'OP':
            if len(stk) < 2:
                raise ValueError('Ошибка вычисления')
            b = stk.pop()
            a = stk.pop()
            
            if v == '+':
                stk.append(a + b)
            elif v == '-':
                stk.append(a - b)
            elif v == '*':
                stk.append(a * b)
            elif v == '/':
                if b == 0:
                    raise ValueError('Деление на ноль')
                stk.append(a / b)
        elif t == 'LOG':
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
print(12.50+(40-90)+.12*2)


