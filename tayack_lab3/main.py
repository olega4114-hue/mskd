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
            
            idx = 0
            while idx < len(line) and line[idx].isupper():
                idx += 1
            
            if idx == 0 or '>' not in line[idx:]:
                raise ValueError(f'Неверный формат правила: {line}')
            
            lhs = line[:idx].strip()
            rest = line[idx:].strip()
            
            if not rest.startswith('>'):
                raise ValueError(f'Неверный формат правила: {line}')
            
            rhs_str = rest[1:].strip()
            rhs = rhs_str.split('|')
            
            if lhs not in rules:
                rules[lhs] = []
            
            if first_nt is None:
                first_nt = lhs
                self.start = lhs
            
            for alt in rhs:
                alt = alt.strip().replace(' ', '')
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
                    if not ch.isupper():
                        terms.add(ch)
        
        for t in terms:
            self.add_cmd2(t)
        
        self.add_cmd3()
        
        return rules, first_nt
    
    def parse_string(self, w):
        visited = set()
        
        def dfs(w_idx, stk_str, depth):
            if depth > 1000:
                return False
            
            key = (w_idx, stk_str)
            if key in visited:
                return False
            visited.add(key)
            
            if w_idx == len(w) and stk_str == 'h0':
                return True
            
            if w_idx > len(w) or len(stk_str) > 100:
                return False
            
            for cmd in self.cmds:
                if cmd[0] == '1':
                    nt, body = cmd[1], cmd[2]
                    if stk_str and stk_str[0] == nt:
                        new_stk = body + stk_str[1:]
                        if dfs(w_idx, new_stk, depth + 1):
                            return True
                
                elif cmd[0] == '2':
                    t = cmd[1]
                    if w_idx < len(w) and w[w_idx] == t and stk_str and stk_str[0] == t:
                        new_stk = stk_str[1:]
                        if dfs(w_idx + 1, new_stk, depth + 1):
                            return True
                
                elif cmd[0] == '3':
                    if w_idx == len(w) and stk_str == 'h0':
                        return True
            
            return False
        
        init_stk = self.start + 'h0'
        result = dfs(0, init_stk, 0)
        return result

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
            
            ok = pda.parse_string(w)
            if ok:
                print(f'Строка "{w}" допускается')
            else:
                print(f'Строка "{w}" не допускается')
    
    except Exception as e:
        print(f'Ошибка: {e}')

if __name__ == '__main__':
    main()
