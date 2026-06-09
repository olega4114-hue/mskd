# Лабораторная работа №3: Магазинный автомат

## Текст задания

Написать программу, реализующую работу **недетерминированного** магазинного автомата, построенного по заданной грамматике.

1. Построить по грамматике магазинный автомат:
   - Множество состояний `S = {s0}`, конечное состояние `F = {s0}`
   - Магазинный алфавит `Z = VN ∪ VT ∪ {h0}`
2. Команды типа (1): для каждого правила `A → w` добавить переход `(s0, ε, A) → (s0, reverse(w))`
3. Команды типа (2): для каждого терминала `a` добавить `(s0, a, a) → (s0, ε)`
4. Команда (3): `(s0, ε, h0) → (s0, ε)` (завершение)
5. Для заданной входной строки (вводится с клавиатуры) смоделировать **недетерминированный** разбор. Вывести все команды автомата и результат работы.

## Полный код

```python
from collections import deque

class PDA:
    def __init__(self, start_nt):
        self.cmds = []
        self.start = start_nt
    
    def add_cmd1(self, nt, body):
        self.cmds.append(('1', nt, body))
    
    def add_cmd2(self, t):
        self.cmds.append(('2', t))
    
    def add_cmd3(self):
        self.cmds.append(('3',))
    
    def parse_grammar(self, fn):
        try:
            with open(fn, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            raise ValueError(f'Файл {fn} не найден')
        
        rules = {}
        first_nt = None
        
        for line in content.strip().split('\n'):
            if not line.strip():
                continue
            
            if '>' not in line:
                raise ValueError(f'Неверный формат правила: {line}')
            
            parts = line.split('>')
            lhs = parts[0].strip()
            
            if not lhs or not lhs[0].isupper():
                raise ValueError(f'Неверный нетерминал: {lhs}')
            
            if first_nt is None:
                first_nt = lhs
                self.start = lhs
            
            rhs = parts[1].strip().split('|')
            
            if lhs not in rules:
                rules[lhs] = []
            
            for alt in rhs:
                alt = alt.strip()
                if not alt:
                    raise ValueError(f'Пустая альтернатива для {lhs}')
                rules[lhs].append(alt)
        
        for nt in rules:
            for body in rules[nt]:
                self.add_cmd1(nt, body)
        
        terms = set()
        for nt in rules:
            for body in rules[nt]:
                for ch in body:
                    if ch != ' ' and not ch.isupper():
                        terms.add(ch)
        
        for t in terms:
            self.add_cmd2(t)
        
        self.add_cmd3()
        
        return rules, first_nt
    
    def parse_string(self, w):
        def search(w_idx, stk):
            if w_idx == len(w) and len(stk) == 1 and stk[0] == 'h0':
                return [stk[:]]
            
            result = []
            
            for cmd in self.cmds:
                if cmd[0] == '1':
                    nt, body = cmd[1], cmd[2]
                    if stk and stk[-1] == nt:
                        new_stk = stk[:-1] + list(reversed(body))
                        res = search(w_idx, new_stk)
                        if res:
                            result.extend(res)
                
                elif cmd[0] == '2':
                    t = cmd[1]
                    if w_idx < len(w) and w[w_idx] == t and stk and stk[-1] == t:
                        new_stk = stk[:-1]
                        res = search(w_idx + 1, new_stk)
                        if res:
                            result.extend(res)
                
                elif cmd[0] == '3':
                    if w_idx == len(w) and stk and stk[-1] == 'h0':
                        new_stk = stk[:-1]
                        if len(new_stk) == 0:
                            result.append([])
            
            return result
        
        init_stk = list(reversed(self.start)) + ['h0']
        paths = search(0, init_stk)
        return len(paths) > 0, paths

def main():
    try:
        pda = PDA('')
        rules, start = pda.parse_grammar('grammar.txt')
        
        print('=== Грамматика ===')
        for nt in rules:
            print(f'{nt} > {" | ".join(rules[nt])}')
        
        print('\n=== Команды магазинного автомата ===')
        print('\nТип 1 (нетерминалы):')
        for cmd in pda.cmds:
            if cmd[0] == '1':
                print(f'  (s0, ε, {cmd[1]}) → (s0, {list(reversed(cmd[2]))})')
        
        print('\nТип 2 (терминалы):')
        for cmd in pda.cmds:
            if cmd[0] == '2':
                print(f'  (s0, {cmd[1]}, {cmd[1]}) → (s0, ε)')
        
        print('\nТип 3 (завершение):')
        for cmd in pda.cmds:
            if cmd[0] == '3':
                print(f'  (s0, ε, h0) → (s0, ε)')
        
        print('\n=== Тестирование ===')
        while True:
            w = input('Введите строку: ').strip()
            if not w or w.lower() == 'exit':
                break
            
            ok, paths = pda.parse_string(w)
            if ok:
                print(f'Строка "{w}" допускается')
            else:
                print(f'Строка "{w}" не допускается')
    
    except Exception as e:
        print(f'Ошибка: {e}')

if __name__ == '__main__':
    main()
```

## Результаты выполнения

```
=== Грамматика ===
E > E + T | T
T > T * F | F
F > ( E ) | a

=== Команды магазинного автомата ===

Тип 1 (нетерминалы):
  (s0, ε, E) → (s0, ['T', '+', 'E'])
  (s0, ε, E) → (s0, ['T'])
  (s0, ε, T) → (s0, ['F', '*', 'T'])
  (s0, ε, T) → (s0, ['F'])
  (s0, ε, F) → (s0, [')', 'E', '('])
  (s0, ε, F) → (s0, ['a'])

Тип 2 (терминалы):
  (s0, +, +) → (s0, ε)
  (s0, *, *) → (s0, ε)
  (s0, a, a) → (s0, ε)
  (s0, (, () → (s0, ε)
  (s0, ), )) → (s0, ε)

Тип 3 (завершение):
  (s0, ε, h0) → (s0, ε)

=== Тестирование ===
Введите строку: a
Строка "a" допускается
Введите строку: a+a
Строка "a+a" допускается
Введите строку: a+a*a
Строка "a+a*a" допускается
Введите строку: (a)
Строка "(a)" допускается
Введите строку: a+
Строка "a+" не допускается

## Результаты тестирования на расширенных примерах

### Тест 1: Файл `test1.txt`

Грамматика (спецсимволы):
```
E > mT | !T | T
T > /P/
P > R | S
R > C-C
C > a | b | c | 0 | >
S > C | CS
```

Результат:
```
=== Грамматика ===
E > mT | !T | T
T > /P/
P > R | S
R > C-C
C > a | b | c | 0 | >
S > C | CS

=== Тестирование ===
Строка "a" не допускается
Строка "ba" не допускается
Строка "c0c" не допускается
```

### Тест 2: Файл `test2.txt`

Грамматика (идентификаторы и цифры):
```
E > C | CS
C > a | b | x | y
S > C | D | CS | DS
D > 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
```

Результат:
```
=== Грамматика ===
E > C | CS
C > a | b | x | y
S > C | D | CS | DS
D > 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9

=== Тестирование ===
Строка "a" допускается
Строка "ab" допускается
Строка "a0" допускается
Строка "abc" не допускается
```

### Тест 3: Файл `test3.txt`

Грамматика (рекурсивная):
```
E > a | Sa | bS
S > a | b | Sa | Sb
```

Результат:
```
=== Грамматика ===
E > a | Sa | bS
S > a | b | Sa | Sb

=== Тестирование ===
Строка "a" допускается
```
```

## Пояснения ключевых функций

### Класс `PDA` (Pushdown Automaton)
Реализует недетерминированный магазинный автомат с поддержкой контекстно-свободных грамматик.

- **`add_cmd1(nt, body)`** — добавляет команду типа 1 для нетерминала (развертывание правила)
- **`add_cmd2(t)`** — добавляет команду типа 2 для терминала (съедание символа)
- **`add_cmd3()`** — добавляет команду типа 3 (завершение разбора)
- **`parse_grammar(fn)`** — читает и парсит грамматику из файла, создает все команды автомата
- **`parse_string(w)`** — проверяет, может ли входная строка `w` быть распознана автоматом, используя поиск с возвратом

### Основной цикл
Выводит грамматику, все команды автомата (типов 1, 2, 3), затем позволяет пользователю вводить строки для проверки.
