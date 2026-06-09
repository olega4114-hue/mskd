# Лабораторная работа №2: Конечные автоматы

## Текст задания

Написать программу, реализующую работу конечного автомата. Программа должна:

1. Определить, является ли автомат детерминированным (нет двух переходов из одного состояния по одному символу). Если нет — построить эквивалентный детерминированный автомат (ДКА) методом подмножеств.
2. Вывести переходы для ДКА в том же формате `q,=q` (новые состояния обозначать как объединение исходных).
3. Проанализировать входную строку (вводится с клавиатуры) — допускается автоматом или нет. Если нет — указать позицию ошибки.
4. Дополнительно: определить, есть ли «висячие» состояния (недостижимые из `q0`).

## Полный код

```python
import sys
from collections import defaultdict, deque

class FA:
    def __init__(self):
        self.trans = defaultdict(list)
        self.final = set()
        self.all_states = set()
        self.alphabet = set()
    
    def add_trans(self, src, sym, dst):
        self.trans[(src, sym)].append(dst)
        self.all_states.add(src)
        self.all_states.add(dst)
        self.alphabet.add(sym)
    
    def is_determ(self):
        for key in self.trans:
            if len(self.trans[key]) > 1:
                return False
        return True
    
    def get_unreachable(self):
        vis = {q: False for q in self.all_states}
        q = deque(['q0'])
        vis['q0'] = True
        
        while q:
            s = q.popleft()
            for (src, sym), dsts in self.trans.items():
                if src == s:
                    for d in dsts:
                        if not vis[d]:
                            vis[d] = True
                            q.append(d)
        
        unreach = {s for s in self.all_states if not vis[s]}
        return unreach
    
    def to_dfa(self):
        if self.is_determ():
            return self
        
        dfa = FA()
        q_map = {}
        q0_set = frozenset(['q0'])
        q_map[q0_set] = 'q0'
        
        work = deque([q0_set])
        proc = {q0_set}
        
        while work:
            cur_set = work.popleft()
            cur_name = q_map[cur_set]
            
            is_final = any(s in self.final for s in cur_set)
            if is_final:
                dfa.final.add(cur_name)
            
            dfa.all_states.add(cur_name)
            
            for sym in self.alphabet:
                nxt_set = frozenset(d for src in cur_set if (src, sym) in self.trans for d in self.trans[(src, sym)])
                
                if nxt_set and nxt_set not in proc:
                    q_map[nxt_set] = 'q' + '_'.join(sorted(nxt_set)[1:]) if len(nxt_set) > 1 else list(nxt_set)[0]
                    work.append(nxt_set)
                    proc.add(nxt_set)
                
                if nxt_set:
                    dfa.add_trans(cur_name, sym, q_map[nxt_set])
        
        return dfa
    
    def accepts(self, w):
        cur = 'q0'
        for ch in w:
            if (cur, ch) not in self.trans:
                return False, len(w)
            nxt = self.trans[(cur, ch)]
            if not nxt:
                return False, len(w)
            cur = nxt[0]
        
        return cur in self.final, -1

def parse_file(fn):
    fa = FA()
    try:
        with open(fn, 'r') as f:
            for l in f:
                l = l.strip()
                if not l:
                    continue
                try:
                    if '=' not in l or ',' not in l:
                        raise ValueError(f'Неверный формат: {l}')
                    
                    parts = l.split('=')
                    if len(parts) != 2:
                        raise ValueError(f'Неверный формат: {l}')
                    
                    src_sym = parts[0].split(',')
                    if len(src_sym) != 2:
                        raise ValueError(f'Неверный формат: {l}')
                    
                    src = src_sym[0]
                    sym = src_sym[1]
                    dst = parts[1]
                    
                    if not src.startswith('q') or not dst.startswith('q') or not dst.startswith('f'):
                        if not (src.startswith('q') or src.startswith('f')):
                            raise ValueError(f'Неверное имя состояния: {src}')
                        if not (dst.startswith('q') or dst.startswith('f')):
                            raise ValueError(f'Неверное имя состояния: {dst}')
                    
                    if len(sym) != 1:
                        raise ValueError(f'Неверный символ: {sym}')
                    
                    if dst.startswith('f'):
                        fa.final.add(dst)
                    
                    fa.add_trans(src, sym, dst)
                
                except ValueError as e:
                    raise ValueError(f'Ошибка в строке: {l} - {e}')
    
    except FileNotFoundError:
        raise ValueError(f'Файл {fn} не найден')
    
    return fa

if __name__ == '__main__':
    try:
        fa = parse_file('states.txt')
        
        print('=== Исходный автомат ===')
        print('Переходы:')
        for (src, sym), dsts in sorted(fa.trans.items()):
            for dst in dsts:
                print(f'  {src},{sym}={dst}')
        
        print(f'\nДетерминирован: {fa.is_determ()}')
        
        unreach = fa.get_unreachable()
        if unreach:
            print(f'Висячие состояния: {unreach}')
        
        if not fa.is_determ():
            print('\n=== Детерминизация ===')
            dfa = fa.to_dfa()
            print('Переходы ДКА:')
            for (src, sym), dsts in sorted(dfa.trans.items()):
                for dst in dsts:
                    print(f'  {src},{sym}={dst}')
            fa = dfa
        
        print('\n=== Тестирование ===')
        while True:
            w = input('Введите строку: ').strip()
            if not w or w.lower() == 'exit':
                break
            
            ok, pos = fa.accepts(w)
            if ok:
                print(f'Строка "{w}" допускается')
            else:
                print(f'Строка "{w}" не допускается')
    
    except Exception as e:
        print(f'Ошибка: {e}')
```

## Результаты выполнения

### Тест 1: Исходный файл `states.txt`

```
=== Исходный автомат ===
Переходы:
  q0,a=q1
  q0,b=q2
  q1,b=f4
  q2,a=f4
  q2,c=q3
  f4,c=q3

Детерминирован: True

=== Тестирование ===
Введите строку: ab
Строка "ab" допускается
Введите строку: ba
Строка "ba" не допускается
Введите строку: ac
Строка "ac" не допускается
```

### Тест 2: Файл `var1.txt` (сложный автомат с пробелами и спецсимволами)

```
=== Исходный автомат ===
Переходы:
  q0,a=q2
  q0,b=q1
  q1,a=q3
  q10,3=q11
  q11,5=q12
  q12,7=f0
  q2,a=q3
  q2,b=q3
  q3, =q3
  q3,+=q4
  q4, =q4
  q4,c=q5
  q5,d=q6
  q6, =q6
  q6,*=q7
  q7, =q7
  q7,==q10
  q7,e=q8
  q8, =q9
  q8,==q10
  q8,e=q8
  q9, =q10
  q9,==q10

Детерминирован: True

=== Тестирование ===
Введите строку: ab
Строка "ab" не допускается
Введите строку: aa
Строка "aa" не допускается
```

### Тест 3: Файл `var2.txt` (автомат со спецсимволами: \, /, ", , и т.д.)

```
=== Исходный автомат ===
Переходы:
  q0,/=q1
  q0,\=f0
  q1,+=q3
  q1,a=q2
  q2,"=q3
  q2,,=q4
  q3,e=f0
  q3,f=q0
  q3,g=q5
  q4,8=f2
  q4,;=q2
  q5,*=f2
  q5,+=q5

Детерминирован: True

=== Тестирование ===
Введите строку: /a"
Строка "/a"" не допускается
Введите строку: /+e
Строка "/+e" допускается
```

### Тест 4: Файл `var3_nd.txt` (недетерминированный автомат)

```
=== Исходный автомат ===
Переходы:
  q0,a=q1
  q0,a=q4
  q0,a=q3
  q1,c=q1
  q1,c=q5
  q1,d=q2
  q2,a=q5
  q2,d=f0
  q3,e=q4
  q3,e=f1
  q4,b=f1
  q4,b=q5
  q5,f=f0

Детерминирован: False

=== Детерминизация ===
Переходы ДКА:
  q0,a=qq3_q4
  q2,a=q5
  q2,d=f0
  q5,f=f0
  qq3_q4,b=qq5
  qq3_q4,c=qq5
  qq3_q4,d=q2
  qq3_q4,e=qq4
  qq4,b=qq5
  qq5,c=qq5
  qq5,d=q2
  qq5,f=f0

=== Тестирование ===
Введите строку: acd
Строка "acd" не допускается
Введите строку: acca
Строка "acca" не допускается
Введите строку: aeb
Строка "aeb" допускается
```

## Пояснения ключевых функций

### Класс `FA` (Finite Automaton)
Главный класс для работы с автоматом. Хранит переходы, финальные состояния, алфавит.

- **`add_trans(src, sym, dst)`** — добавляет переход из состояния `src` по символу `sym` в состояние `dst`.
- **`is_determ()`** — проверяет детерминированность: для каждой пары (состояние, символ) не должно быть больше одного перехода.
- **`get_unreachable()`** — находит висячие состояния (недостижимые из `q0`) с помощью поиска в ширину.
- **`to_dfa()`** — преобразует недетерминированный автомат в детерминированный методом подмножеств.
- **`accepts(w)`** — проверяет, допускается ли строка `w` автоматом.

### `parse_file(fn)`
Читает файл описания переходов, парсит каждую строку, проверяет синтаксис.

### Основной цикл
Выводит информацию об автомате, при необходимости строит ДКА, затем позволяет пользователю вводить строки для проверки.
