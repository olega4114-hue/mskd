import math

priority = {'(': 1, '+': 2, '-':2, '*':3, '/': 3, '^':4, 'log':5}

def expression(a, b, operation):
    if operation == '+':
        return a + b
    elif operation == '-':
        return a - b
    elif operation == '*':
        return a * b
    elif operation == '/':
        if b == 0:
            return 'Некорректный ввод: на 0 делить нельзя'
        return a / b
    elif operation == '^':
        return a ** b
    elif operation == 'log':
        return math.log(a, b)
    else:
        return 'Некорректный ввод: не поддерживаемый оператор'


def calculate(input_string):
    if input_string.count('(') != input_string.count(')'):
        return 'Некорректный ввод: неверно расставлены скобки'
    if '++' in input_string or '--' in input_string or '**' in input_string or '//' in input_string or '..' in input_string:
        return 'Некорректный ввод:арифметические символы дублируют друг друга( ** или -- и т.д.)'
    input_string = input_string.replace(' ', '')

    stack = []
    res = []
    num = ''
    input_len = len(input_string)
    idx = 0
    log_args = 1

    while idx < input_len:
        if input_string[idx].isdigit() or input_string[idx] == '.':
            num += input_string[idx]
            if idx == input_len - 1:
                res.append(num)

        else:
            if num!= '':
                res.append(num)
            num = ''
            if input_string[idx] == 'l' and idx + 3 < input_len:
                if input_string[idx:idx+3] == 'log':
                    stack.append('log')
                    log_args = 1

                    idx += 2
                else:
                    return 'Некорректный ввод: озможно вы имели в виду log'
            elif not stack or input_string[idx] == '(':
                stack.append(input_string[idx])

            elif input_string[idx] == ')':
                while stack and stack[-1] != '(':
                    res.append(stack.pop())
                stack.pop()

            elif input_string[idx] == ',' and stack[-2] == 'log':
                log_args += 1
                if log_args > 2:
                    return 'Некорректный ввод: log имеет только 2 аргумента log(a,b)'

            else:
                while stack and priority[stack[-1]] >= priority[input_string[idx]]:
                    res.append(stack.pop())
                stack.append(input_string[idx])


        idx += 1

    rpn = res + stack [::-1]
    print(rpn)
    stack = []
    for item in rpn:
        if item.isdigit() or '.' in item:
            stack.append(float(item))
        elif item in {'+', '-', '*', '/', '^', 'log'}:
            b = stack.pop()
            a = stack.pop()
            result = expression(a, b, item)
            if type(result) == str:
                return result
            stack.append(result)

    return stack.pop()



#'12.50+(40-90)+.12*2'
#'(10+11)*(12+13)-14'
#'3+4*2/(1-5)^2'
#'log(10, 2) + 3 * 5'

print(calculate('12.50+(40-90)+.12*2'))
print(12.50+(40-90)+.12*2)


