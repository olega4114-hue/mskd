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
                if not l or l.startswith(';'):
                    continue
                try:
                    if '=' not in l or ',' not in l:
                        raise ValueError(f'Неверный формат: {l}')
                    
                    comma_idx = l.index(',')
                    eq_idx = l.rindex('=')
                    
                    src = l[:comma_idx].strip()
                    sym = l[comma_idx+1:eq_idx].strip()
                    if not sym:
                        sym = l[comma_idx+1:eq_idx]
                    dst = l[eq_idx+1:].strip()
                    
                    if not (src.startswith('q') or src.startswith('f')):
                        raise ValueError(f'Неверное имя состояния: {src}')
                    if not (dst.startswith('q') or dst.startswith('f')):
                        raise ValueError(f'Неверное имя состояния: {dst}')
                    
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
